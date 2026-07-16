"""
label_tool.py — Step 3 of Phase 1: manual labeling helper.

A lightweight, single-review-at-a-time Streamlit UI for labeling the 200 sampled
reviews with human ground truth (true_sentiment + true_severity). The labeler sees
ONLY the review text, app, and rating — never the model's prediction — so labels
are unbiased. Autosaves after every entry and resumes where you left off.

Run:
    streamlit run dashboard/label_tool.py

Output:
    data/labels/labels.csv  (review_id, true_sentiment, true_severity, notes)

Prefer a spreadsheet instead? Just open data/labels/label_queue_blind.csv in Excel
and fill the true_sentiment / true_severity columns by hand — the validation
notebook reads either source.
"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_BLIND = os.path.join(REPO, "data", "labels", "label_queue_blind.csv")
LABELS_CSV = os.path.join(REPO, "data", "labels", "labels.csv")

SENTIMENTS = ["Negative", "Neutral", "Positive"]
SEVERITY_RUBRIC = {
    5: "Critical — money lost/inaccessible, account locked/closed, fraud",
    4: "High — core function broken: transfer/verification/card failure",
    3: "Moderate — friction, needs support, refund/delay disputes",
    2: "Low-Moderate — annoyance, bugs, UX complaints",
    1: "Low — minor/neutral/positive, no operational failure",
}

st.set_page_config(page_title="Review Labeler", page_icon="🏷️", layout="centered")


# ---------------------------------------------------------------------------
# Data loading / persistence
# ---------------------------------------------------------------------------
@st.cache_data
def load_queue() -> pd.DataFrame:
    return pd.read_csv(QUEUE_BLIND)


def load_labels() -> pd.DataFrame:
    if os.path.exists(LABELS_CSV):
        return pd.read_csv(LABELS_CSV)
    return pd.DataFrame(columns=["review_id", "true_sentiment", "true_severity", "notes"])


def save_label(review_id, sentiment, severity, notes) -> None:
    labels = load_labels()
    labels = labels[labels["review_id"] != review_id]  # overwrite if re-labeling
    new = pd.DataFrame([{
        "review_id": review_id,
        "true_sentiment": sentiment,
        "true_severity": int(severity),
        "notes": notes,
    }])
    labels = pd.concat([labels, new], ignore_index=True)
    os.makedirs(os.path.dirname(LABELS_CSV), exist_ok=True)
    labels.to_csv(LABELS_CSV, index=False)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
queue = load_queue()
labels = load_labels()
done_ids = set(labels["review_id"].tolist())

st.title("🏷️ Fintech Review Labeler")

remaining = queue[~queue["review_id"].isin(done_ids)]
n_done, n_total = len(done_ids), len(queue)

st.progress(n_done / n_total if n_total else 0.0)
st.caption(f"{n_done} / {n_total} labeled")

# Jump-to control in the sidebar (review any index, incl. already-labeled ones).
with st.sidebar:
    st.header("Navigation")
    mode = st.radio("Show", ["Next unlabeled", "Jump to row #"])
    if mode == "Jump to row #":
        idx = st.number_input("Row (0-based)", 0, n_total - 1, 0, 1)
        current = queue.iloc[int(idx)]
    else:
        if remaining.empty:
            current = None
        else:
            current = remaining.iloc[0]
            idx = queue.index[queue["review_id"] == current["review_id"]][0]

    st.divider()
    st.subheader("Severity rubric")
    for score in (5, 4, 3, 2, 1):
        st.markdown(f"**{score}** — {SEVERITY_RUBRIC[score]}")

if current is None:
    st.success("✅ All 200 reviews labeled! Run notebook 10 to compute metrics.")
    st.download_button("⬇️ Download labels.csv", load_labels().to_csv(index=False),
                       "labels.csv", "text/csv")
    st.stop()

# --- Review card (prediction intentionally hidden) ---
existing = labels[labels["review_id"] == current["review_id"]]
st.markdown(f"### Row {int(idx)} · {current['app_name']} · {'⭐' * int(current['rating'])}")
st.info(current["review_text"])

with st.form(key=f"label_{current['review_id']}"):
    default_sent = existing["true_sentiment"].iloc[0] if len(existing) else "Negative"
    default_sev = int(existing["true_severity"].iloc[0]) if len(existing) else 3
    default_notes = existing["notes"].iloc[0] if len(existing) and pd.notna(existing["notes"].iloc[0]) else ""

    sentiment = st.radio("True sentiment", SENTIMENTS,
                         index=SENTIMENTS.index(default_sent), horizontal=True)
    severity = st.select_slider(
        "True severity", options=[1, 2, 3, 4, 5], value=default_sev,
        format_func=lambda s: f"{s} · {SEVERITY_RUBRIC[s].split(' — ')[0].split(' ')[0]}")
    st.caption(SEVERITY_RUBRIC[severity])
    notes = st.text_input("Notes (optional)", value=default_notes)

    submitted = st.form_submit_button("💾 Save & next", use_container_width=True)
    if submitted:
        save_label(current["review_id"], sentiment, severity, notes)
        st.rerun()
