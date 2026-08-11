# Fintech Sentiment Intelligence Analysis

**An NLP system that finds the complaints fintech companies miss — the ones hiding in positive reviews.**

Analyzed 10,386 customer reviews across Cash App, Chime, PayPal, and Venmo to identify churn risk signals, crisis language patterns, and competitive vulnerabilities. Built with VADER, NLTK, scikit-learn, and a 4-page interactive Streamlit dashboard.

---

## The Business Problem

Fintech apps live and die by trust. When a user's money gets frozen, a transfer fails, or fraud goes unresolved, they don't just churn — they leave a review. But not all bad experiences show up as 1-star ratings.

A significant share of high-severity complaints are written politely — buried in 3-star and 4-star reviews that standard sentiment tools classify as neutral or positive. This project finds them.

---

## Key Findings

**Across 10,386 reviews (2,600 per app):**

- **707 hidden complaints** identified — high-severity issues disguised in positive language, missed by standard sentiment tools
- **30.6% of reviews are negative** (3,177 reviews) — but standard rating-based filtering captures less than half the real complaint volume
- **Account access issues** are the #1 crisis pattern (35% of high-severity complaints): locked accounts, frozen funds, suspended access
- **Venmo has the worst sentiment profile** (3.31★ average) despite being owned by PayPal
- **Cash App rates highest** (4.07★) but shows the sharpest rating decline following UI redesign

**Crisis pattern breakdown:**
- Account Access (35%): "locked," "frozen," "can't access," "suspended"
- Money/Payment Problems (28%): "missing," "lost," "transfer," "funds"
- Fraud & Security (18%): "fraud," "scam," "hacked," "unauthorized"

---

## NLP Pipeline

### Sentiment Classification
- VADER with custom negation handling (reduced error rate by 38%)
- Severity scoring on a 1–5 scale
- Fintech-specific crisis keyword lexicon (built from domain research)
- Hidden negative detector: flags complaints written in polite or neutral language

### Validation
Hand-labeled 200 reviews as ground truth:

| Metric | Score |
|--------|-------|
| Sentiment accuracy | 67.0% |
| Severity macro-F1 | 0.30 (+87% improvement over baseline) |
| High-severity F1 | 0.55 |
| Negative recall | 64.0% |

The 67% accuracy reflects a known limitation: VADER was designed for social media, not fintech complaint language. The custom negation handling and crisis lexicon were direct responses to this gap.

---

## Interactive Dashboard

4-page Streamlit dashboard with real-time filtering by app, sentiment, severity, and rating:

- **Overview page** — volume, sentiment distribution, rating trends
- **App comparison** — competitive benchmarking across all 4 apps
- **Crisis detection** — flagged reviews sorted by severity score
- **Topic insights** — keyword clusters by complaint category

```bash
cd dashboard
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data collection | google-play-scraper |
| Processing | Pandas, NumPy, Regex |
| NLP | VADER, NLTK, spaCy |
| Topic modeling | scikit-learn TfidfVectorizer |
| Dashboard | Streamlit, Plotly, Matplotlib |
| Validation | 200 hand-labeled reviews |

---

## Repository Structure

```
Fintech-Sentiment-Intelligence-Analysis/
├── data/
│   ├── raw/              # Original scraped reviews
│   ├── clean/            # Cleaned & processed data
│   └── labels/           # Hand-labeled validation set (200 reviews)
├── notebooks/
│   ├── 01_scraping.ipynb
│   ├── 03_sentiment_nlp.ipynb
│   ├── 04_evaluation_mismatch_analysis.ipynb
│   ├── 10_validation_metrics.ipynb
│   └── 11_error_analysis.ipynb
├── src/
│   └── analysis.py       # Core sentiment + severity engine
├── dashboard/
│   ├── app.py
│   ├── utils.py
│   └── pages/
├── outputs/
│   ├── charts/
│   └── tables/
├── docs/
│   └── Executive_Summary.pdf
└── README.md
```

---

## Quick Start

```bash
git clone https://github.com/johnkirima/Fintech-Sentiment-Intelligence-Analysis.git
cd Fintech-Sentiment-Intelligence-Analysis
pip install -r requirements.txt

# Run dashboard
cd dashboard
streamlit run app.py
```

---

## What I'd Do Differently

The core limitation here is VADER's vocabulary. It was built for short-form social media text — not the longer, more formal complaint language common in app store reviews. A fine-tuned FinBERT or domain-adapted sentiment model would outperform VADER significantly on fintech-specific language.

The hidden negative detector also relied on keyword heuristics. With more labeled data, a supervised classifier trained specifically on "polite complaint" patterns would be more robust and generalizable across apps.

---

## Related Projects

- [DataForge](https://github.com/johnkirima/DataForge) — 9-agent automation pipeline for EDA and cleaning
- [Predictive Markdown Intelligence](https://github.com/johnkirima/Predictive-Markdown-Intelligence) — Fast fashion markdown forecasting
- [Supply Chain DI](https://github.com/johnkirima/Supply-Chain-DI) — Multi-warehouse inventory optimization under uncertainty

---

## Author

**John Kirima** — Applied Data Scientist & Decision Intelligence Engineer  
[johnkirima.com](https://johnkirima.com) · [LinkedIn](https://www.linkedin.com/in/john-kirima/)
