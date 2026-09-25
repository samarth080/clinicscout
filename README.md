# ClinicScout

Turns a hospital web page into the structured fields needed to judge it as a pilot site.

**Live app:** https://clinicscout.vercel.app

**Source:** https://github.com/samarth080/clinicscout

Built after doing the research by hand. Fifteen institutions were classified manually for
Part 2, and the same three questions came up every time: does this hospital actually do
joint replacement, who runs it, and does rehab sit in the same building. Roughly six
minutes a page, most of it spent reading marketing copy to find out that the page never
says. That is the job this automates.

---

## Mini-PRD

**Problem.** Building a pilot longlist means reading dozens of hospital pages that are
written to sell, not to inform. The expensive part is not reading — it is not being
fooled. "Advanced knee care centre" and "total knee replacement" look the same at a
glance, and a directory page will happily give you a surgeon who left two years ago.

**User.** Founder or founder's-office operator building a pilot pipeline.

**Job to be done.** Convert an unstructured hospital page into structured, evidence-backed
fields that can be pasted straight into the institution longlist.

**Input.** A URL, or pasted page text for sites that block fetching.

**Output.** Seven fields, each with a value, a verbatim quote from the page, and a flag
if the claim was rejected: joint replacement offered, knee replacement mentioned, hip
replacement mentioned, rehab capability, orthopaedic lead, physiotherapy lead, volume
signal. Plus phone numbers found by regex. JSON and CSV export.

**Success criteria.** Low hallucination rate first, coverage second. A tool that says
Unknown too often costs a minute of manual checking; a tool that invents a surgeon costs
the credibility of the whole sheet.

**Non-goals.** Estimating procedure volumes the page does not state. Inferring a
clinician's current role from a third-party directory. Scoring pilot fit (that judgement
stays with the human and the Part 2 weighting model). Any contact with patient data —
the tool only ever reads public institutional pages.

---

## How it avoids making things up

Two mechanisms, both applied after the model returns:

1. **Evidence verification.** Every non-Unknown field must carry a verbatim quote. Each
   quote is checked as a substring of the page text after whitespace and case
   normalisation. If the quote is not in the page, the field is reset to Unknown and
   flagged `evidence_not_found`. Inventing a fact now requires inventing a quote that
   survives a string match against the source.

2. **Term gating.** A knee or hip replacement claim is only accepted if the evidence
   quote itself contains a replacement or arthroplasty term. "Knee care", "knee pain
   clinic", "sports injury" and "physiotherapy for knees" do not pass. Names are checked
   against the page too (`name_not_on_page`).

Both are deliberately dumb and deterministic. They are checks on the model, so they must
not depend on the model.

---

## Setup

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here  # never committed; see below
streamlit run app.py
```

**Deploy (Vercel):** import the repository, then add `GEMINI_API_KEY` under *Project
Settings → Environment Variables*. `public/` is the framework-free browser interface and
`api/scout.py` is the only serverless function; it imports `extractor.py`, so the web app
and evaluation use the same extraction and verification code. The key is read only by
the server and is never returned to, stored by, or logged in the browser. Keyword mode
works without a key, and model mode visibly falls back to it if the key is unavailable.

The public endpoint accepts only public HTTP(S) URLs, caps request bodies at 256 KB and
model input at 18,000 characters, times out model work after 42 seconds, and applies a
best-effort limit of 20 requests per IP per hour. The counter is in memory and therefore
per warm Vercel instance; a globally strict counter would require shared storage, which
is deliberately out of scope for this small no-database tool.

**Model.** Defaults to Gemini 3.5 Flash-Lite (`CLINICSCOUT_GEMINI_MODEL` to override), which has
a documented free API tier and structured JSON output. Free-tier requests may be used
to improve Google's products, so the existing public-institutional-pages-only rule is
important: no patient data is accepted or needed. Extraction with a strict schema is a
small-model job; paying for a large one here is waste.

**Error handling.** Fetch failures, JavaScript-only pages (under 200 characters of text),
malformed JSON and API errors all degrade to the keyword baseline with the reason shown
on screen, rather than failing silently or returning a confident wrong answer.

---

## Evaluation

```bash
python eval/run_eval.py --mode baseline    # naive keyword arm
python eval/run_eval.py                    # model + verification
python eval/run_eval.py --cache eval/pages # score saved page text, no network
```

**Benchmark: 20 items** — the 18 institutions from the Part 2 universe plus two physio
clinics as hard negatives. The labels in `eval/ground_truth.csv` were written while
building the institution longlist, **before this tool existed**, so the benchmark cannot
have been tuned to flatter it.

Three items are deliberately awkward:

- **Physio Synapse** — a physiotherapy clinic whose page is entirely about knee
  replacement rehabilitation. Mentions knee replacement constantly; performs no surgery.
- **CHPL** — its page gives roughly 20 Oxford *partial* knee replacements a month, a
  procedure our TKR definition excludes. The tool should report the figure with its
  wording, not quietly bank it as total knee volume.
- **Healing Hospital** — a "15,000+ joint replacements" claim that is cumulative
  marketing, not annual volume.

**Scoring.** For yes/no fields only "Yes" counts as an assertion, so "No" and "Unknown"
are both treated as abstentions. Three verdicts: `correct`, `over_abstained` (missed
something the page did say — a coverage cost) and `hallucination` (asserted something the
label contradicts — the expensive kind). Pages that cannot be read count against the
tool; a page it cannot open is a page it cannot help with.

**Before running:** fill the `url` column in `eval/ground_truth.csv` from the
Claim_Ledger, and re-read the three rows marked `recheck_before_scoring = YES`. Those
labels came from a call or a paper rather than from the page, and ground truth for a page
reader must describe what the page says.

The current baseline run scored all 20 institutions and 100 field-level judgements:
34% correct and 66% error, comprising 3% hallucinations, 8% over-abstentions and 55%
unreadable/missing-page errors. Eleven of the 20 official pages could not be read. This
is intentionally harsh: infrastructure failure is still failure for the user.

The verified Gemini arm scored 35% correct and 65% error on the same 100 judgements:
4% hallucinations, 6% over-abstentions and the same 55% unreadable/missing-page errors.
It beat the keyword arm by one judgement, mostly by extracting named leads, but that
small gain is not a strong result. Official-site availability dominates both arms.

One scored name error is worth reading carefully: the Paras Panchkula page names
Dr. Jagandeep Virk as Associate Director and Dr. Ravi Kumar Gupta as Chairman and HOD.
The locked label expects Dr. Virk; the model selected the more senior title and therefore
scores as a hallucination. I did not alter this unflagged label after seeing the output.

---

## A failure the benchmark caught, and the fix

**Before.** Testing the harness on a hand-written negative fixture — a general hospital
listing an ophthalmology department and a knee pain clinic, with no arthroplasty service —
the keyword gate marked it a joint-replacement provider. The fixture is not a scraped page.

**Why.** The replacement-term list was matched as plain substrings, and it included the
abbreviations `tka`, `thr` and `tha`. "Tha" sits inside **ophthalmology**. The page
mentions its ophthalmology department, the matcher read that as total hip arthroplasty,
and the hospital was promoted to a surgical site. The same list gated the verified model
path, so a model quote containing "ophthalmology" would have passed too.

**Fix.** Split the list: long words (`replacement`, `arthroplasty`, `resurfacing`) stay
substring matches; the abbreviations now match only on word boundaries via regex.

**After.** GMSH-16 returns No on all three replacement fields. `TKA and THA` in real text
still matches. The fix is in `extractor.py::has_replacement_term`.

Worth noting what this says about method rather than code: the bug was invisible when
reading outputs one page at a time, because GMSH-16 looked like a plausible hospital.
It only surfaced when a page with a known-negative label was run through the harness.

### A second failure: failed pages vanished from the score

**Before.** The first live baseline run reported 24% error: 34 correct, 3 hallucinations
and 8 over-abstentions across only 45 judgements from nine institutions. Seven attempted
pages had failed to load, and four rows had no official URL, but none of those 11
institutions appeared in the denominator even though the evaluation notes said failed
pages counted against the tool.

**Why.** `run_eval.py` filtered out blank URLs before scoring and used `continue` after a
fetch failure. It recorded a console message, not five field-level failures. The summary
therefore measured only the easiest readable subset.

**Fix.** The harness now loads all 20 rows. A missing URL, failed fetch, missing cache, or
too-short page emits five explicit `unreadable` verdicts and is listed in the summary.
The original result is preserved under `eval/before_fix/`, and an offline regression
check proves that one unreadable institution creates five scored errors.

**After.** The same baseline has 66% error across all 100 judgements: 34 correct, 3
hallucinations, 8 over-abstentions, and 55 unreadable/missing-page errors. Model quality
did not get worse; the denominator became honest.

---

## Known limitations

- Results vary by about one judgement between runs even at temperature 0 (35–36 of 100
  correct).
- A correct Ojas rehab answer was rejected because "physio center" is not in the rehab
  word list.
- Long pages are cut at 18,000 characters, which likely caused the Park Grecian knee/hip
  misses.
- **One page, not one hospital.** Rehab often lives on a different URL from orthopaedics,
  so a hospital can score Unknown on rehab while having a physiotherapy department.
  Feed both pages, or accept the undercount.
- **JavaScript-rendered sites** return too little text and are reported as unreadable
  rather than guessed at.
- **Official-site availability dominates this small benchmark.** Eleven of 20 pages were
  missing or blocked in the recorded run, so 55 of 100 field judgements are unreadable
  errors before extraction quality is considered.
- **The public rate limit is best effort.** It is enforced per warm serverless instance,
  not globally, because the project intentionally has no database or paid infrastructure.
- **Currency.** The tool reads what the page says today. It cannot tell that a page is
  two years stale — the Livasa rebrand and the Dhillon role change were both caught by a
  human, not by this.
- **Volume signals are reported, not interpreted.** Distinguishing cumulative from annual,
  or partial from total knee, is left to the reader. The tool quotes the wording so the
  reader can tell.
- **The abstention rate is the honest cost.** On thin pages this returns a lot of
  Unknowns. That is the intended trade: manual checking is cheap, a fabricated surgeon in
  a founder's outreach sheet is not.
