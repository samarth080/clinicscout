import io
import json
import os

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from extractor import FIELDS, scout

st.set_page_config(page_title="ClinicScout", page_icon="🩺", layout="wide")

LABELS = {
    "joint_replacement_offered": "Joint replacement offered",
    "knee_replacement_mentioned": "Knee replacement mentioned",
    "hip_replacement_mentioned": "Hip replacement mentioned",
    "rehab_capability": "Rehab / physiotherapy capability",
    "ortho_lead": "Orthopaedic lead named",
    "physio_lead": "Physiotherapy lead named",
    "volume_signal": "Volume signal",
}


def api_key() -> str:
    env_key = os.environ.get("GEMINI_API_KEY", "")
    try:
        return st.secrets.get("GEMINI_API_KEY", env_key)
    except StreamlitSecretNotFoundError:
        # A clean local checkout has no secrets file. That is a supported state:
        # the UI should load and let the user run the keyword baseline.
        return env_key


st.title("ClinicScout")
st.caption(
    "Turns a hospital page into structured pilot-research fields. "
    "Built for one job: cutting the time it takes to work out whether a hospital "
    "actually does joint replacement, who runs it, and whether rehab sits in the same "
    "building. It answers Unknown whenever the page does not say — every claim it makes "
    "is backed by a quote that is checked against the page."
)

with st.sidebar:
    st.subheader("Settings")
    mode = st.radio("Extraction mode", ["Model + verification", "Keyword baseline"],
                    help="The baseline is the naive keyword matcher used as the "
                         "comparison arm in the evaluation.")
    st.markdown("---")
    st.markdown(
        "**What it will not do**\n\n"
        "- estimate procedure volumes that the page does not state\n"
        "- infer a surgeon's current role from a directory\n"
        "- treat 'knee care' or 'joint pain' as knee replacement\n"
        "- touch patient data of any kind"
    )
    if not api_key():
        st.warning("No API key found. Set GEMINI_API_KEY in Streamlit secrets, or use "
                   "the keyword baseline.")

tab1, tab2 = st.tabs(["Single page", "Batch"])

with tab1:
    col1, col2 = st.columns([3, 1])
    url = col1.text_input("Hospital page URL", placeholder="https://example-hospital.com/orthopaedics")
    pasted = st.text_area("…or paste the page text instead (for pages that block fetching)",
                          height=120)
    if col2.button("Run", type="primary", use_container_width=True):
        if not url and not pasted:
            st.error("Give a URL or paste some text.")
        else:
            with st.spinner("Reading the page…"):
                res = scout(url or "pasted text", api_key=api_key(),
                            raw_text=pasted or None,
                            mode="baseline" if mode.startswith("Keyword") else "llm")
            if not res.ok:
                st.error(res.error)
            else:
                if res.error:
                    st.warning(f"Fell back to the baseline: {res.error}")
                rows = []
                for f in FIELDS:
                    fr = res.fields[f]
                    rows.append({
                        "Field": LABELS[f],
                        "Value": fr.value,
                        "Verified": "yes" if fr.verified and fr.value != "Unknown" else "",
                        "Flag": fr.flag,
                        "Evidence from the page": (fr.evidence[:300] if fr.value != "Unknown" else ""),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                c1, c2 = st.columns(2)
                c1.metric("Fields answered", f"{len(FIELDS) - len(res.missing)}/{len(FIELDS)}")
                c2.metric("Phone numbers found on page", len(res.contact_phones))
                if res.contact_phones:
                    st.write("Numbers on the page (regex, not model): "
                             + ", ".join(res.contact_phones))
                if res.missing:
                    st.info("Unknown, so the page did not say it: "
                            + ", ".join(LABELS[m] for m in res.missing))
                st.download_button("Download JSON",
                                   json.dumps(res.as_dict(), indent=2),
                                   file_name="clinicscout.json")

with tab2:
    st.write("One URL per line. Output matches the Institution_Universe columns.")
    urls = st.text_area("URLs", height=160)
    if st.button("Run batch", type="primary"):
        lines = [u.strip() for u in urls.splitlines() if u.strip()]
        if not lines:
            st.error("No URLs.")
        else:
            out, bar = [], st.progress(0.0)
            for i, u in enumerate(lines, start=1):
                r = scout(u, api_key=api_key(),
                          mode="baseline" if mode.startswith("Keyword") else "llm")
                row = {"url": u, "ok": r.ok, "error": r.error,
                       "phones": "; ".join(r.contact_phones)}
                for f in FIELDS:
                    row[f] = r.fields[f].value if r.ok else ""
                    row[f + "_flag"] = r.fields[f].flag if r.ok else ""
                out.append(row)
                bar.progress(i / len(lines))
            df = pd.DataFrame(out)
            st.dataframe(df, use_container_width=True, hide_index=True)
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            st.download_button("Download CSV", buf.getvalue(), file_name="clinicscout_batch.csv")
