"""Offline self-check. Exercises the paths that cannot be reached without an API key
or live network, using a mocked API response and synthetic HTML.
Run: python tests_selfcheck.py
"""
import json, sys, types
import extractor as E
from eval.run_eval import unreadable_rows

PAGE_HTML = """
<html><head><title>Ortho</title><style>.x{}</style></head><body>
<nav>Home | Departments</nav>
<h1>Department of Orthopaedics &amp; Joint Replacement</h1>
<p>Our team performs total knee replacement and total hip replacement using
navigation-assisted techniques. Dr. Ramesh Verma heads the joint replacement unit.</p>
<p>Our physiotherapy department provides post-operative rehabilitation and a
home exercise programme. Call 0172-4692222 for appointments.</p>
<script>var a=1;</script></body></html>
"""

FAKE_MODEL_TEXT = "```json\n" + json.dumps({
    "joint_replacement_offered": {"value": "Yes",
        "evidence": "Our team performs total knee replacement and total hip replacement"},
    "knee_replacement_mentioned": {"value": "Yes",
        "evidence": "performs total knee replacement"},
    "hip_replacement_mentioned": {"value": "Yes",
        "evidence": "total hip replacement using navigation-assisted techniques"},
    "rehab_capability": {"value": "Yes",
        "evidence": "Our physiotherapy department provides post-operative rehabilitation"},
    # deliberately fabricated: this sentence is NOT on the page
    "ortho_lead": {"value": "Dr. Anil Kapoor",
        "evidence": "Dr. Anil Kapoor is the senior arthroplasty consultant"},
    "physio_lead": {"value": "Unknown", "evidence": ""},
    # a real quote, but it does not support a volume claim
    "volume_signal": {"value": "500 surgeries per year",
        "evidence": "Department of Orthopaedics & Joint Replacement"},
}) + "\n```"
FAKE_MODEL_REPLY = {
    "candidates": [{"content": {"parts": [{"text": FAKE_MODEL_TEXT}]}}]
}

class FakeResp:
    status_code = 200
    def raise_for_status(self): pass
    def json(self): return FAKE_MODEL_REPLY

def fake_post(*a, **k): return FakeResp()

fails = []
checks = 0

def check(name, cond, detail=""):
    global checks
    checks += 1
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail else ""))
    if not cond: fails.append(name)

# 1. HTML handling without network
text = E.html_to_text(PAGE_HTML)
check("html_to_text strips script/style", "var a=1" not in text and ".x{}" not in text)
check("html_to_text keeps body copy", "total knee replacement" in text)
check("phone regex finds the number", "01724692222" in E.find_phones(text))

# 2. Model path with a mocked API
E.requests.post = fake_post
res = E.scout("mock://page", api_key="test-key", raw_text=PAGE_HTML)
f = res.fields
check("fenced JSON parsed", res.ok and res.mode == "llm", res.error)
check("true field accepted", f["knee_replacement_mentioned"].value == "Yes")
check("hip accepted", f["hip_replacement_mentioned"].value == "Yes")
check("rehab accepted", f["rehab_capability"].value == "Yes")
check("fabricated name rejected",
      f["ortho_lead"].value == "Unknown" and f["ortho_lead"].flag == "evidence_not_found",
      f["ortho_lead"].flag)
check("unsupported volume quote rejected", f["volume_signal"].value == "Unknown")
check("abstention preserved", f["physio_lead"].value == "Unknown")

# 3. Non-patient contexts must not count as clinical capability
internship_quote = "Application Form for Six months Physiotherapy Intership with Orthopaedics Department"
internship = E.verify({
    "rehab_capability": {"value": "Yes", "evidence": internship_quote},
}, internship_quote)
check("internship form rejected as non-patient context",
      internship["rehab_capability"].value == "Unknown"
      and internship["rehab_capability"].flag == "non_patient_context",
      internship["rehab_capability"].flag)

service_quote = "post-operative rehabilitation after joint replacement"
patient_service = E.verify({
    "rehab_capability": {"value": "Yes", "evidence": service_quote},
}, service_quote)
check("genuine patient rehabilitation remains accepted",
      patient_service["rehab_capability"].value == "Yes")

# 4. Failure handling
def boom(*a, **k): raise RuntimeError("429 rate limited")
E.requests.post = boom
res2 = E.scout("mock://page", api_key="test-key", raw_text=PAGE_HTML)
check("API failure degrades to baseline, not a crash",
      res2.ok and res2.mode.startswith("baseline") and "429" in res2.error)

res3 = E.scout("mock://tiny", api_key="test-key", raw_text="too short")
check("thin/JS page reported, not guessed", not res3.ok and "too short" in res3.error)

# 5. The bug the benchmark caught
check("ophthalmology no longer reads as arthroplasty",
      not E.has_replacement_term("Department of ophthalmology and ENT"))
check("real abbreviations still match", E.has_replacement_term("we perform TKA and THA"))

# 6. Evaluation failures must remain in the denominator
unreadable = unreadable_rows({"inst_id": "X", "institution": "Blocked"}, "403 blocked")
check("unreadable page becomes five scored errors",
      len(unreadable) == 5 and all(r["verdict"] == "unreadable" for r in unreadable))

print("\n%d checks, %d failed" % (checks, len(fails)))
sys.exit(1 if fails else 0)
