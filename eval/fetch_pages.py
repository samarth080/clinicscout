"""Fetch and cache the benchmark pages using the same code path as ClinicScout."""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor import fetch_page, html_to_text  # noqa: E402


HERE = os.path.dirname(__file__)
TRUTH = os.path.join(HERE, "ground_truth.csv")
PAGES = os.path.join(HERE, "pages")
MANIFEST = os.path.join(HERE, "fetch_manifest.csv")


def main():
    os.makedirs(PAGES, exist_ok=True)
    with open(TRUTH, newline="", encoding="utf-8") as fh:
        truth_rows = list(csv.DictReader(fh))

    manifest = []
    for row in truth_rows:
        inst_id, url = row["inst_id"], row.get("url", "").strip()
        entry = {"inst_id": inst_id, "institution": row["institution"],
                 "url": url, "status": "", "page_chars": "", "error": ""}
        if not url:
            entry.update(status="missing_url", error="no official page found")
            manifest.append(entry)
            print(f"{inst_id}: missing official page")
            continue
        try:
            text = html_to_text(fetch_page(url))
            path = os.path.join(PAGES, f"{inst_id}.txt")
            with open(path, "w", encoding="utf-8") as out:
                out.write(text + "\n")
            entry.update(status="ok" if len(text) >= 200 else "too_short",
                         page_chars=str(len(text)))
            if len(text) < 200:
                entry["error"] = "page text too short — likely JavaScript-rendered or blocked"
            manifest.append(entry)
            print(f"{inst_id}: {entry['status']} ({len(text)} chars)")
        except Exception as exc:
            entry.update(status="fetch_failed", error=str(exc)[:500])
            manifest.append(entry)
            print(f"{inst_id}: fetch failed: {exc}")

    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()
