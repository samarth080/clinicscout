from __future__ import annotations

import ipaddress
import json
import os
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from extractor import MAX_PAGE_CHARS, scout


RATE_LIMIT = 20
RATE_WINDOW_SECONDS = 60 * 60
MAX_REQUEST_BYTES = 256_000
MAX_PASTED_CHARS = 50_000
REQUEST_TIMEOUT_SECONDS = 42

_requests_by_ip: dict[str, list[float]] = {}
_rate_lock = threading.Lock()


def _client_ip(headers) -> str:
    forwarded = headers.get("x-forwarded-for", "")
    return (forwarded.split(",", 1)[0].strip() or
            headers.get("x-real-ip", "unknown"))


def _rate_allowed(ip: str) -> bool:
    now = time.time()
    cutoff = now - RATE_WINDOW_SECONDS
    with _rate_lock:
        recent = [stamp for stamp in _requests_by_ip.get(ip, []) if stamp > cutoff]
        if len(recent) >= RATE_LIMIT:
            _requests_by_ip[ip] = recent
            return False
        recent.append(now)
        _requests_by_ip[ip] = recent
        if len(_requests_by_ip) > 10_000:
            _requests_by_ip.clear()
            _requests_by_ip[ip] = [now]
    return True


def _public_http_url(value: str) -> bool:
    """Reject local/private fetch targets; the endpoint is for public pages only."""
    try:
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False
        if parsed.username or parsed.password:
            return False
        for info in socket.getaddrinfo(parsed.hostname, parsed.port or 443):
            address = ipaddress.ip_address(info[4][0])
            if not address.is_global:
                return False
        return True
    except (OSError, ValueError):
        return False


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("allow", "POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        self._send_json(200, {"ok": True, "service": "ClinicScout",
                              "model_page_char_cap": MAX_PAGE_CHARS})

    def do_POST(self):
        if not _rate_allowed(_client_ip(self.headers)):
            self._send_json(429, {
                "ok": False,
                "error": "Rate limit reached. Please try again in about an hour.",
            })
            return

        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_REQUEST_BYTES:
            self._send_json(413, {"ok": False, "error": "Request is empty or too large."})
            return

        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"ok": False, "error": "Send a valid JSON request."})
            return

        url = str(payload.get("url", "") or "").strip()
        pasted = str(payload.get("text", "") or "").strip()
        mode = "baseline" if payload.get("mode") == "baseline" else "llm"
        if not url and not pasted:
            self._send_json(400, {"ok": False, "error": "Give a public URL or paste page text."})
            return
        if len(pasted) > MAX_PASTED_CHARS:
            self._send_json(413, {"ok": False, "error": "Pasted text is limited to 50,000 characters."})
            return
        if url and not pasted and (len(url) > 2_048 or not _public_http_url(url)):
            self._send_json(400, {"ok": False, "error": "Use a valid public http(s) URL."})
            return

        key = os.environ.get("ANTHROPIC_API_KEY", "")
        degraded_reason = ""
        if mode == "llm" and not key:
            mode = "baseline"
            degraded_reason = "Model unavailable because the server API key is not configured; used the keyword baseline."

        def run():
            return scout(url or "pasted text", api_key=key, raw_text=pasted or None,
                         mode=mode, fetch_timeout=12, model_timeout=30)

        pool = ThreadPoolExecutor(max_workers=1)
        try:
            result = pool.submit(run).result(timeout=REQUEST_TIMEOUT_SECONDS)
        except TimeoutError:
            pool.shutdown(wait=False, cancel_futures=True)
            self._send_json(504, {
                "ok": False,
                "error": "The page or model took too long. Try the keyword baseline or paste the page text.",
            })
            return
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

        data = result.as_dict()
        if degraded_reason:
            data["error"] = degraded_reason
        self._send_json(200 if result.ok else 422, data)

