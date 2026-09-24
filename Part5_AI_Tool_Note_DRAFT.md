# Part 5 — ClinicScout

**Link:** [deployed app URL]  ·  **Code:** [repo URL]  ·  **Screen recording:** [link]

**What it does.** Reads a hospital web page and returns seven structured fields — joint
replacement offered, knee and hip replacement mentioned, rehab capability, orthopaedic
lead, physiotherapy lead, volume signal — each with a verbatim quote from the page, plus
any phone numbers found. JSON and CSV out, straight into the Part 2 longlist columns.

**Why this and not something cleverer.** I classified fifteen institutions by hand for
Part 2 and kept answering the same three questions: does this hospital actually do
arthroplasty, who runs it, does rehab sit in the same building. About six minutes a page,
most of it spent discovering the page never says. The scoring and ranking stayed manual
on purpose — that is judgement, and the weights carry my reasoning, not a model's.

**How it avoids inventing things.** Two checks run after the model, both deterministic,
because a check that depends on the model is not a check. First, every non-Unknown field
must carry a verbatim quote, and each quote is string-matched against the page; if it
isn't there, the field is reset to Unknown and flagged. Second, a knee or hip replacement
claim is only accepted if the quote itself contains a replacement or arthroplasty term —
"knee care" and "knee pain clinic" do not pass. Names are checked against the page too.

**How I tested it.** A 20-item benchmark: the 18 institutions from my Part 2 universe plus
two physiotherapy clinics as hard negatives. The labels were written while building that
longlist, before the tool existed, so the benchmark could not be tuned to flatter it.
Three items are deliberately awkward — a physio clinic whose page is all about knee
replacement but performs no surgery, a hospital whose only volume figure is for *partial*
knees (excluded by my TKR definition), and a "15,000+ joint replacements" cumulative
marketing claim. I scored the model against a naive keyword matcher to check the model was
earning its place.

**Results.** Error rate [X]% across [N] field-level judgements ([Y] hallucinations, [Z]
over-abstentions). The keyword baseline scored [B]%, failing mainly by [how]. Per-field
numbers and every failure are in `eval/summary_llm.md`; the run is reproducible with
`python eval/run_eval.py`.

**A failure I caught and fixed.** The baseline classified Government Multi Specialty
Hospital Sector 16 as a joint-replacement provider. It has no arthroplasty service — the
page lists a knee *pain* clinic. Cause: the replacement-term list was matched as plain
substrings and included the abbreviation "tha", which sits inside **ophthalmology**. The
page mentions its ophthalmology department and the hospital was promoted to a surgical
site. The same list gated the verified model path, so a model quote containing that word
would have passed too. Fix: long words stay substring matches, abbreviations now match
only on word boundaries. After the fix GMSH-16 returns No on all three replacement fields
while "TKA and THA" in real text still matches. The bug was invisible reading outputs one
page at a time — GMSH-16 looked like a plausible hospital — and only surfaced because the
benchmark included a page with a known-negative label.

**What it gets wrong.** It reads one page, not one hospital, so a site whose rehab lives
on a separate URL scores Unknown on rehab. JavaScript-rendered pages return too little
text and are reported unreadable rather than guessed at. It cannot tell a stale page from
a current one — the Livasa rebrand and a director's role change were both caught by me,
not by it. It reports volume signals without interpreting them, so separating cumulative
from annual, or partial from total knee, is still the reader's job. And it returns a lot
of Unknowns on thin pages. That is the intended trade: a minute of manual checking is
cheap, a fabricated surgeon in a founder's outreach sheet is not.

**No patient data of any kind is used. The tool only reads public institutional pages.**
