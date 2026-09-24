"""
Scores ClinicScout against hand-labelled ground truth.

The labels in eval/ground_truth.csv were written while building the Part 2 institution
universe, BEFORE this tool existed. That ordering is the point: the benchmark cannot be
tuned to flatter the tool.

Usage
    python eval/run_eval.py                 # model + verification
    python eval/run_eval.py --mode baseline # naive keyword arm
    python eval/run_eval.py --cache eval/pages   # use saved page text, no network

Outputs
    eval/results_<mode>.csv   one row per institution per field
    eval/summary_<mode>.md    accuracy per field, hallucination rate, abstention quality
"""

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor import FIELDS, scout  # noqa: E402

SCORED = ["joint_replacement_offered", "knee_replacement_mentioned",
          "hip_replacement_mentioned", "rehab_capability", "ortho_lead"]


def norm(v):
    return (v or "").strip().lower()


BOOLEAN_FIELDS = {"joint_replacement_offered", "knee_replacement_mentioned",
                  "hip_replacement_mentioned", "rehab_capability"}
ABSTAIN = {"", "unknown"}


def judge(field, truth, got):
    """Returns (verdict, failure_type).

    correct        - matches the label
    correct_unknown- label is Unknown and the tool abstained
    over_abstained - label has a value, tool said Unknown (a miss, not a lie)
    hallucination  - tool asserted something the label contradicts
    """
    t, g = norm(truth), norm(got)
    # For yes/no fields, "No" and "Unknown" are both non-assertions: the tool is not
    # claiming the page says something. Only "Yes" is an assertion.
    if field in BOOLEAN_FIELDS:
        t_assert, g_assert = t == "yes", g == "yes"
        if t_assert and g_assert:
            return "correct", ""
        if not t_assert and not g_assert:
            return "correct_unknown", ""
        if g_assert:
            return "hallucination", "asserted_over_unknown"
        return "over_abstained", "missed"
    if t in ABSTAIN:
        return ("correct_unknown", "") if g in ABSTAIN else ("hallucination", "asserted_over_unknown")
    if g in ABSTAIN:
        return "over_abstained", "missed"
    if field in ("ortho_lead", "physio_lead"):
        tl = t.replace("dr.", "").replace("prof.", "").strip().split(";")[0].split()
        return ("correct", "") if tl and tl[-1] in g else ("hallucination", "wrong_name")
    return ("correct", "") if t == g else ("hallucination", "wrong_value")


def unreadable_rows(tr, reason):
    """Turn a page-level failure into scored errors instead of dropping the page."""
    return [{
        "inst_id": tr["inst_id"], "institution": tr["institution"], "field": f,
        "ground_truth": tr.get(f, ""), "tool_output": "Unknown",
        "verdict": "unreadable", "failure_type": "page_unreadable",
        "flag": reason[:200], "evidence": "",
    } for f in SCORED]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="llm", choices=["llm", "baseline"])
    ap.add_argument("--cache", default=None, help="directory of <inst_id>.txt page dumps")
    ap.add_argument("--truth", default=os.path.join(os.path.dirname(__file__), "ground_truth.csv"))
    args = ap.parse_args()

    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if args.mode == "llm" and not key:
        sys.exit("Set ANTHROPIC_API_KEY, or run with --mode baseline.")

    with open(args.truth, newline="", encoding="utf-8") as fh:
        truth_rows = list(csv.DictReader(fh))

    if not truth_rows:
        sys.exit("No ground-truth rows found.")

    rows, skipped = [], []
    for tr in truth_rows:
        raw = None
        if args.cache:
            path = os.path.join(args.cache, f"{tr['inst_id']}.txt")
            if not os.path.exists(path):
                reason = "no cached page"
                skipped.append((tr["institution"], reason))
                rows.extend(unreadable_rows(tr, reason))
                continue
            raw = open(path, encoding="utf-8").read()
        elif not tr.get("url"):
            reason = "no official page found"
            skipped.append((tr["institution"], reason))
            rows.extend(unreadable_rows(tr, reason))
            continue

        res = scout(tr.get("url") or tr["institution"], api_key=key,
                    raw_text=raw, mode=args.mode)
        if not res.ok:
            skipped.append((tr["institution"], res.error))
            rows.extend(unreadable_rows(tr, res.error))
            continue

        for f in SCORED:
            got = res.fields[f].value
            verdict, ftype = judge(f, tr.get(f, ""), got)
            rows.append({
                "inst_id": tr["inst_id"], "institution": tr["institution"], "field": f,
                "ground_truth": tr.get(f, ""), "tool_output": got,
                "verdict": verdict, "failure_type": ftype,
                "flag": res.fields[f].flag,
                "evidence": res.fields[f].evidence[:200],
            })
        time.sleep(0.4)

    out_csv = os.path.join(os.path.dirname(__file__), f"results_{args.mode}.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    correct = sum(r["verdict"].startswith("correct") for r in rows)
    halluc = sum(r["verdict"] == "hallucination" for r in rows)
    over = sum(r["verdict"] == "over_abstained" for r in rows)
    unreadable = sum(r["verdict"] == "unreadable" for r in rows)

    lines = [f"# ClinicScout evaluation — mode: {args.mode}", "",
             f"Institutions scored: {len({r['inst_id'] for r in rows})}  |  "
             f"field-level judgements: {n}", "",
             f"- Correct: {correct}/{n} ({correct / n:.0%})",
             f"- **Error rate: {(n - correct) / n:.0%}**",
             f"- Hallucination rate (asserted something wrong): {halluc}/{n} ({halluc / n:.0%})",
             f"- Over-abstained (said Unknown when the page did say it): {over}/{n} ({over / n:.0%})",
             f"- Unreadable or missing page: {unreadable}/{n} ({unreadable / n:.0%})",
             "", "## Per field", "", "| Field | Correct | Hallucinated | Over-abstained | Unreadable |",
             "|---|---|---|---|---|"]
    for f in SCORED:
        sub = [r for r in rows if r["field"] == f]
        if sub:
            c = sum(r["verdict"].startswith("correct") for r in sub)
            h = sum(r["verdict"] == "hallucination" for r in sub)
            o = sum(r["verdict"] == "over_abstained" for r in sub)
            u = sum(r["verdict"] == "unreadable" for r in sub)
            lines.append(f"| {f} | {c}/{len(sub)} | {h} | {o} | {u} |")

    fails = [r for r in rows if not r["verdict"].startswith("correct")]
    if fails:
        lines += ["", "## Every failure, listed", "",
                  "| Institution | Field | Ground truth | Tool said | Type | Flag |",
                  "|---|---|---|---|---|---|"]
        for r in fails:
            lines.append(f"| {r['institution']} | {r['field']} | {r['ground_truth']} | "
                         f"{r['tool_output']} | {r['failure_type']} | {r['flag']} |")
    if skipped:
        lines += ["", "## Pages that could not be read", ""]
        lines += [f"- {i}: {why}" for i, why in skipped]
        lines += ["", "Each unreadable or missing page contributes five errors: a page "
                      "the tool cannot read is a page it cannot help with."]

    out_md = os.path.join(os.path.dirname(__file__), f"summary_{args.mode}.md")
    open(out_md, "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {out_csv} and {out_md}")


if __name__ == "__main__":
    main()
