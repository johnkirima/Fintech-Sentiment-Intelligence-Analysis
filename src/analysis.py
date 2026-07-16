"""
analysis.py — Single source of truth for the Fintech Sentiment Intelligence engine.

Consolidates the VADER sentiment logic and the rule-based Severity Engine that were
previously duplicated inline across notebooks 03/05/06/07. The labeling sampler,
the validation notebook, and the Streamlit dashboard all import from here so there
is zero drift between what the notebooks report and what the dashboard shows.

Usage
-----
    from src.analysis import score_dataframe
    df = score_dataframe(pd.read_csv("data/clean/all_apps_clean.csv"))

    # or piece by piece:
    from src.analysis import get_vader_score, vader_label, compute_severity
"""

from __future__ import annotations

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------------------------------
# VADER sentiment
# ---------------------------------------------------------------------------
# A single shared analyzer instance (thread-safe for read-only scoring).
_ANALYZER = SentimentIntensityAnalyzer()

# Thresholds are the VADER-recommended defaults, matching notebook 05.
VADER_POS_THRESHOLD = 0.05
VADER_NEG_THRESHOLD = -0.05


def get_vader_score(text) -> float:
    """Return VADER compound score in [-1, 1]. NaN/empty -> 0.0."""
    if pd.isna(text):
        return 0.0
    return _ANALYZER.polarity_scores(str(text))["compound"]


def vader_label(compound: float) -> str:
    """Map a VADER compound score to Positive / Neutral / Negative."""
    if compound >= VADER_POS_THRESHOLD:
        return "Positive"
    if compound <= VADER_NEG_THRESHOLD:
        return "Negative"
    return "Neutral"


def rating_label(rating) -> str:
    """Map a 1-5 star rating to sentiment tiers (the 'ground truth' proxy)."""
    if pd.isna(rating):
        return "Neutral"
    if rating >= 4:
        return "Positive"
    if rating <= 2:
        return "Negative"
    return "Neutral"


# ---------------------------------------------------------------------------
# Fintech Severity Engine (rule-based keyword lexicon)
# ---------------------------------------------------------------------------
# First match wins, scanning level 5 (Critical) down to 1 (Low). Default = 1.
SEVERITY_KEYWORDS = {
    5: ["locked out", "account locked", "account closed", "money missing",
        "funds missing", "stolen", "fraud", "scam", "cannot access",
        "lost my money", "money gone", "unauthorized"],
    4: ["declined", "card declined", "transfer failed", "verification failed",
        "failed", "frozen", "pending", "verification", "can't send",
        "can't receive", "not working", "blocked"],
    3: ["customer service", "support", "refund", "delay", "late",
        "problem", "issue", "error", "wrong", "charge"],
    2: ["slow", "bug", "glitch", "annoying", "confusing", "difficult"],
    1: ["minor", "small", "slight", "okay", "fine"],
}

SEVERITY_MAP = {1: "Low", 2: "Low-Moderate", 3: "Moderate", 4: "High", 5: "Critical"}

# Convenience: ordered labels high -> low for consistent chart/table ordering.
SEVERITY_ORDER = ["Critical", "High", "Moderate", "Low-Moderate", "Low"]


def compute_severity(text) -> int:
    """Rule-based severity score 1-5 from complaint keywords. NaN -> 1 (Low)."""
    if pd.isna(text):
        return 1
    text = str(text).lower()
    for level in (5, 4, 3, 2, 1):
        for kw in SEVERITY_KEYWORDS[level]:
            if kw in text:
                return level
    return 1


def severity_label(score: int) -> str:
    """Map a 1-5 severity score to its human label."""
    return SEVERITY_MAP.get(int(score), "Low")


# ---------------------------------------------------------------------------
# One-call scoring
# ---------------------------------------------------------------------------
def score_dataframe(df: pd.DataFrame, text_col: str = "review_clean",
                    rating_col: str = "rating") -> pd.DataFrame:
    """
    Add all derived scoring columns in one pass. Returns a copy.

    Adds:
        vader_compound, vader_sentiment, rating_sentiment,
        severity_score, severity_label, is_hidden_negative, is_high_severity
    """
    out = df.copy()
    out["vader_compound"] = out[text_col].apply(get_vader_score)
    out["vader_sentiment"] = out["vader_compound"].apply(vader_label)
    out["rating_sentiment"] = out[rating_col].apply(rating_label)
    out["severity_score"] = out[text_col].apply(compute_severity)
    out["severity_label"] = out["severity_score"].map(SEVERITY_MAP)

    # A "hidden negative" = truly negative (by rating) but VADER did NOT flag it.
    out["is_hidden_negative"] = (
        (out["rating_sentiment"] == "Negative") &
        (out["vader_sentiment"] != "Negative")
    )
    # Binary high-severity detector — the framing the $2-4M business case rests on.
    out["is_high_severity"] = out["severity_score"] >= 4
    return out


if __name__ == "__main__":
    # Smoke test / CLI: score the clean dataset and print a summary.
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    csv = os.path.join(here, "..", "data", "clean", "all_apps_clean.csv")
    df = score_dataframe(pd.read_csv(csv))
    print(f"Scored {len(df):,} reviews")
    print("\nSeverity distribution:")
    print(df["severity_label"].value_counts().reindex(SEVERITY_ORDER))
    print("\nHidden negatives:", int(df["is_hidden_negative"].sum()))
    print("High-severity reviews:", int(df["is_high_severity"].sum()))
