"""
build_label_sample.py — Step 2 of Phase 1.

Draws a reproducible, STRATIFIED sample of 200 reviews for manual labeling so we
can validate the Severity Engine and VADER against human ground truth.

Why stratified (not random)?
    A pure random 200 would be ~59% 5-star reviews with almost no Critical cases,
    making it useless for validating the severity engine. We deliberately oversample
    negative-rating and predicted-high-severity reviews so every metric (esp.
    high-severity recall) has enough positives to be meaningful.

Outputs (to data/labels/):
    label_queue.csv        full 200 rows WITH model predictions (used at scoring time)
    label_queue_blind.csv  same 200 rows WITHOUT predictions (used for unbiased labeling)

Run:
    python scripts/build_label_sample.py
"""

from __future__ import annotations

import os
import sys

import pandas as pd

# Make `src` importable whether run from repo root or scripts/.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from src.analysis import score_dataframe  # noqa: E402

SEED = 42
TARGET_TOTAL = 200
PER_APP = 50  # 4 apps x 50 = 200

CLEAN_CSV = os.path.join(REPO, "data", "clean", "all_apps_clean.csv")
LABELS_DIR = os.path.join(REPO, "data", "labels")

# Within each app's 50, aim for this rating-tier mix (approx 60/15/25).
TIER_TARGETS = {"Negative": 30, "Neutral": 7, "Positive": 13}


def _sample_tier(pool: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    """Sample up to n rows, oversampling predicted high-severity first."""
    if len(pool) <= n:
        return pool
    high = pool[pool["is_high_severity"]]
    rest = pool[~pool["is_high_severity"]]
    # Take up to half the quota from high-severity (guarantees positives), rest random.
    n_high = min(len(high), n // 2)
    picked_high = high.sample(n=n_high, random_state=seed) if n_high else high.iloc[:0]
    n_rest = n - len(picked_high)
    picked_rest = rest.sample(n=min(len(rest), n_rest), random_state=seed)
    return pd.concat([picked_high, picked_rest])


def build_sample() -> pd.DataFrame:
    df = score_dataframe(pd.read_csv(CLEAN_CSV))

    frames = []
    for app in sorted(df["app_name"].unique()):
        app_df = df[df["app_name"] == app]
        for tier, n in TIER_TARGETS.items():
            pool = app_df[app_df["rating_sentiment"] == tier]
            frames.append(_sample_tier(pool, n, SEED))

    sample = pd.concat(frames).drop_duplicates(subset="review_id")

    # Top up to exactly TARGET_TOTAL if rounding/dedup left us short.
    if len(sample) < TARGET_TOTAL:
        remaining = df[~df["review_id"].isin(sample["review_id"])]
        topup = remaining.sample(n=TARGET_TOTAL - len(sample), random_state=SEED)
        sample = pd.concat([sample, topup])

    sample = (sample.sample(frac=1, random_state=SEED)  # shuffle so labeling order is mixed
              .head(TARGET_TOTAL)
              .reset_index(drop=True))
    return sample


def main() -> None:
    os.makedirs(LABELS_DIR, exist_ok=True)
    sample = build_sample()

    # Full queue WITH predictions (for scoring later).
    queue_cols = ["review_id", "app_name", "rating", "review_text",
                  "vader_sentiment", "severity_score", "severity_label",
                  "is_hidden_negative"]
    queue = sample[queue_cols].copy()
    queue["true_sentiment"] = ""   # to be filled: Negative / Neutral / Positive
    queue["true_severity"] = ""    # to be filled: 1-5
    queue["notes"] = ""
    queue.to_csv(os.path.join(LABELS_DIR, "label_queue.csv"), index=False)

    # Blind queue WITHOUT predictions (so the labeler is not anchored).
    blind = sample[["review_id", "app_name", "rating", "review_text"]].copy()
    blind["true_sentiment"] = ""
    blind["true_severity"] = ""
    blind["notes"] = ""
    blind.to_csv(os.path.join(LABELS_DIR, "label_queue_blind.csv"), index=False)

    # Report coverage so we can eyeball that stratification worked.
    print(f"Sampled {len(sample)} reviews (seed={SEED})")
    print("\nBy app:")
    print(sample["app_name"].value_counts())
    print("\nBy rating tier:")
    print(sample["rating_sentiment"].value_counts())
    print("\nBy predicted severity:")
    print(sample["severity_label"].value_counts().reindex(
        ["Critical", "High", "Moderate", "Low-Moderate", "Low"], fill_value=0))
    print(f"\nPredicted hidden negatives in sample: {int(sample['is_hidden_negative'].sum())}")
    print(f"Predicted high-severity in sample    : {int(sample['is_high_severity'].sum())}")
    print(f"\nWrote:\n  {os.path.join(LABELS_DIR, 'label_queue.csv')}"
          f"\n  {os.path.join(LABELS_DIR, 'label_queue_blind.csv')}")


if __name__ == "__main__":
    main()
