"""
ClinicScout — turns a hospital web page into structured pilot-research fields.

Design rule: the tool must prefer "Unknown" over a guess. Two mechanisms enforce that.

1. Evidence verification. The model must return a verbatim quote for every non-Unknown
   field. After the call, each quote is checked against the page text. If the quote is
   not actually in the page, the field is reset to Unknown and flagged. A model that
   invents a surgeon cannot also invent a quote that survives this check.

2. Term gating. Detecting knee/hip replacement requires a replacement or arthroplasty
   term inside the evidence quote itself. "Knee care", "knee pain clinic" and
   "joint pain" do not qualify. This is the fix for the failure described in the notes.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict, field
from typing import Optional

import requests
from bs4 import BeautifulSoup

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("CLINICSCOUT_MODEL", "claude-haiku-4-5-20251001")
MAX_PAGE_CHARS = 18000

# Long terms are safe as substrings. The abbreviations are NOT: "tha" is inside
# "ophthalmology", "thal" and "that", and "tka"/"thr" hide inside other words too.
# Found by running the benchmark — see the failure note in README.md.
REPLACEMENT_WORDS = ["replacement", "arthroplasty", "resurfacing"]
REPLACEMENT_ABBREV = ["tkr", "tka", "thr", "tha", "uka", "ukr"]
REPLACEMENT_ABBREV_RE = re.compile(r"\b(" + "|".join(REPLACEMENT_ABBREV) + r")\b", re.I)


def has_replacement_term(text: str) -> bool:
    low = text.lower()
    return any(w in low for w in REPLACEMENT_WORDS) or bool(REPLACEMENT_ABBREV_RE.search(text))


REPLACEMENT_TERMS = REPLACEMENT_WORDS + REPLACEMENT_ABBREV  # kept for display only
KNEE_TERMS = ["knee"]
HIP_TERMS = ["hip"]
REHAB_TERMS = [
    "physiotherapy", "physiotherapist", "physical therapy", "rehabilitation",
    "rehab", "domiciliary", "home visit",
]
PHONE_CANDIDATE_RE = re.compile(r"(?<![\d])[+(]?\d[\d\s\-()]{8,18}\d(?![\d])")

FIELDS = [
    "joint_replacement_offered",
    "knee_replacement_mentioned",
    "hip_replacement_mentioned",
    "rehab_capability",
    "ortho_lead",
    "physio_lead",
    "volume_signal",
]

SYSTEM_PROMPT = """You extract facts from hospital web pages for pilot-site research.

Rules, in order of importance:
1. If the page does not clearly state something, answer "Unknown". Unknown is a correct
   answer and is always better than a guess.
2. Every field that is not "Unknown" must come with `evidence`: a VERBATIM quote copied
   character-for-character from the page text. Do not paraphrase, do not reconstruct,
   do not tidy punctuation. Quotes are checked against the page automatically and a
   field whose quote cannot be found is discarded.
3. Knee or hip REPLACEMENT means arthroplasty. General orthopaedics, knee pain clinics,
   sports injury, arthroscopy and physiotherapy for knees are NOT knee replacement.
   Only answer Yes if the evidence quote itself says replacement or arthroplasty.
4. Names must be people named on this page. Give the name exactly as printed.
5. A volume signal is an explicit count of procedures or surgeries. A bed count, a
   patient-footfall number, a "years of experience" figure and a cumulative career
   total are NOT annual procedure volumes. If the page gives a cumulative or career
   figure, report it and say so in the evidence.

Return ONLY a JSON object, no preamble and no markdown fences, shaped exactly like:
{
  "joint_replacement_offered": {"value": "Yes|No|Unknown", "evidence": "..."},
  "knee_replacement_mentioned": {"value": "Yes|No|Unknown", "evidence": "..."},
  "hip_replacement_mentioned": {"value": "Yes|No|Unknown", "evidence": "..."},
  "rehab_capability": {"value": "Yes|No|Unknown", "evidence": "..."},
  "ortho_lead": {"value": "<name>|Unknown", "evidence": "..."},
  "physio_lead": {"value": "<name>|Unknown", "evidence": "..."},
  "volume_signal": {"value": "<figure as printed>|Unknown", "evidence": "..."}
}
Use "" for evidence when the value is Unknown."""


@dataclass
class FieldResult:
    value: str = "Unknown"
    evidence: str = ""
    verified: bool = False
    flag: str = ""


@dataclass
class ScoutResult:
    source: str = ""
    ok: bool = True
    error: str = ""
    mode: str = "llm"
    page_chars: int = 0
    contact_phones: list = field(default_factory=list)
    fields: dict = field(default_factory=dict)
    missing: list = field(default_factory=list)

    def as_dict(self):
        d = asdict(self)
        d["fields"] = {k: asdict(v) if isinstance(v, FieldResult) else v
                       for k, v in self.fields.items()}
        return d


# ---------------------------------------------------------------- page handling

def fetch_page(url: str, timeout: int = 20) -> str:
    headers = {"User-Agent": "ClinicScout/1.0 (student research project)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return normalise(text)


def normalise(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2013", "-")
    return re.sub(r"\s+", " ", text).strip()


def find_phones(text: str, limit: int = 3) -> list:
    """Indian numbers come in several shapes: +91 plus ten digits, an STD code with a
    six-to-eight digit local number, or a bare ten-digit mobile. Rather than one clever
    pattern, take digit-ish runs and validate the digit count."""
    out = []
    for m in PHONE_CANDIDATE_RE.finditer(text):
        d = re.sub(r"\D", "", m.group())
        if d.startswith("91") and len(d) == 12:
            ok = True
        elif d.startswith("0") and 10 <= len(d) <= 12:
            ok = True
        elif len(d) == 10 and d[0] in "6789":
            ok = True
        else:
            ok = False
        if ok and d not in out:
            out.append(d)
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------- verification

def quote_in_page(quote: str, page: str) -> bool:
    """Substring check after normalising whitespace and case."""
    if not quote or len(quote.strip()) < 8:
        return False
    return normalise(quote).lower() in page.lower()


def term_gate(fname: str, evidence: str) -> Optional[str]:
    """Return a flag string if the evidence does not support the claim."""
    ev = evidence.lower()
    has_repl = has_replacement_term(evidence)
    if fname in ("joint_replacement_offered", "knee_replacement_mentioned",
                 "hip_replacement_mentioned") and not has_repl:
        return "no_replacement_term_in_evidence"
    if fname == "knee_replacement_mentioned" and not any(t in ev for t in KNEE_TERMS):
        return "no_knee_term_in_evidence"
    if fname == "hip_replacement_mentioned" and not any(t in ev for t in HIP_TERMS):
        return "no_hip_term_in_evidence"
    if fname == "rehab_capability" and not any(t in ev for t in REHAB_TERMS):
        return "no_rehab_term_in_evidence"
    return None


def verify(raw: dict, page: str) -> dict:
    """Apply evidence verification and term gating to the model's raw JSON."""
    out = {}
    for fname in FIELDS:
        item = raw.get(fname) or {}
        value = str(item.get("value", "Unknown")).strip() or "Unknown"
        evidence = str(item.get("evidence", "") or "")
        res = FieldResult(value=value, evidence=evidence)

        if value.lower() in ("unknown", "no", ""):
            res.value = "Unknown" if value.lower() in ("unknown", "") else value
            res.verified = True          # an abstention needs no evidence
            out[fname] = res
            continue

        if not quote_in_page(evidence, page):
            out[fname] = FieldResult("Unknown", evidence, False, "evidence_not_found")
            continue

        gate = term_gate(fname, evidence)
        if gate:
            out[fname] = FieldResult("Unknown", evidence, False, gate)
            continue

        if fname in ("ortho_lead", "physio_lead"):
            surname = value.replace("Dr.", "").replace("Prof.", "").strip().split(" ")[-1]
            if surname and surname.lower() not in page.lower():
                out[fname] = FieldResult("Unknown", evidence, False, "name_not_on_page")
                continue

        res.verified = True
        out[fname] = res
    return out


# ---------------------------------------------------------------- baseline

def keyword_baseline(page: str) -> dict:
    """Deterministic comparison arm. Deliberately naive: it looks for the words and
    does not read context. Used in the evaluation to show what the model adds."""
    low = page.lower()
    out = {}

    def yesno(cond):
        return FieldResult("Yes" if cond else "No", "", True, "baseline")

    repl = has_replacement_term(page)
    out["knee_replacement_mentioned"] = yesno("knee" in low and repl)
    out["hip_replacement_mentioned"] = yesno("hip" in low and repl)
    out["joint_replacement_offered"] = yesno(repl)
    out["rehab_capability"] = yesno(any(t in low for t in REHAB_TERMS))
    for f in ("ortho_lead", "physio_lead", "volume_signal"):
        out[f] = FieldResult("Unknown", "", True, "baseline")
    return out


# ---------------------------------------------------------------- model call

def call_model(page: str, api_key: str, model: str = MODEL, timeout: int = 60) -> dict:
    body = {
        "model": model,
        "max_tokens": 1200,
        "system": SYSTEM_PROMPT,
        "messages": [{
            "role": "user",
            "content": f"PAGE TEXT:\n\n{page[:MAX_PAGE_CHARS]}\n\nReturn the JSON object now."
        }],
    }
    r = requests.post(
        API_URL,
        headers={"x-api-key": api_key,
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json=body, timeout=timeout,
    )
    r.raise_for_status()
    text = "".join(blk.get("text", "") for blk in r.json().get("content", []))
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)


# ---------------------------------------------------------------- entry point

def scout(source: str, api_key: Optional[str] = None, raw_text: Optional[str] = None,
          mode: str = "llm", fetch_timeout: int = 20,
          model_timeout: int = 60) -> ScoutResult:
    """source: a URL (or a label, when raw_text is supplied)."""
    res = ScoutResult(source=source, mode=mode)
    try:
        page = (normalise(raw_text) if raw_text else
                html_to_text(fetch_page(source, timeout=fetch_timeout)))
    except Exception as exc:
        return ScoutResult(source=source, ok=False, error=f"fetch failed: {exc}", mode=mode)

    res.page_chars = len(page)
    if res.page_chars < 200:
        res.ok = False
        res.error = "page text too short — likely JavaScript-rendered or blocked"
        return res

    res.contact_phones = find_phones(page)

    if mode == "baseline":
        res.fields = keyword_baseline(page)
    else:
        if not api_key:
            res.ok = False
            res.error = "no API key set"
            return res
        try:
            res.fields = verify(call_model(page, api_key, timeout=model_timeout), page)
        except Exception as exc:
            # fall back rather than dying: a degraded answer that says so is usable
            res.mode = "baseline (model call failed)"
            res.error = str(exc)[:200]
            res.fields = keyword_baseline(page)

    res.missing = [f for f, v in res.fields.items() if v.value == "Unknown"]
    return res
