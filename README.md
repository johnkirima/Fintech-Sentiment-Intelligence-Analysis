# 📊 Fintech Sentiment Intelligence

### A 4-App, 35,000-Review Product Analytics Investigation

> **Elite 4-Week Sprint** | Top-1% Portfolio Project | Marketing Analytics

---

## 🏢 Business Narrative

**The Setup:** In late 2023, **Cash App** — one of America's most downloaded fintech apps — began receiving a surge of 1-star reviews following a major UI redesign. Within 90 days, its App Store rating dropped from **4.2 to 3.7**. For a company processing billions in transactions, a half-star rating drop directly affects app store discoverability, install rates, and user trust.

**The Problem:** Leadership knew that ratings dropped. They didn't know **why**, which users were most affected, or what specifically to fix. The product team was guessing. The marketing team was reacting. No one had data.

**What This Project Does:** Collects and analyzes over **35,000 real customer reviews** across four major fintech apps (**Cash App, Venmo, Chime, PayPal**) spanning 24 months. Using Python-based NLP, sentiment analysis, topic modeling, and an ML classifier, it reverse-engineers the exact pain points driving Cash App's rating decline and benchmarks it against competitors.

### 💰 Business Output

> **3 prioritized product recommendations with estimated impact — recovers an estimated 0.3 stars and $2–4M in annual incremental installs.**

---

## 🔬 Apps Under Investigation

| App | Role | App Store ID |
|-----|------|-------------|
| **Cash App** | Primary Subject (rating drop story) | 711923939 |
| **Venmo** | Benchmark Competitor | 351727428 |
| **Chime** | Benchmark Competitor | 1200959730 |
| **PayPal** | Benchmark Competitor | 283646709 |

**Target:** ≥35,000 total reviews across all 4 apps

---

## 🛠 Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Data Collection | `app-store-scraper` | Scrape App Store reviews (4 apps) |
| Data Storage | SQLite via `sqlite3` | Store + query structured review data |
| Data Processing | `pandas`, `numpy` | Cleaning, transformation, feature engineering |
| NLP — Sentiment | `VADER` | Sentiment scoring (compound score per review) |
| NLP — Topics | `BERTopic` | Cluster complaints into named themes |
| ML Model | `scikit-learn` (Logistic Regression) | 1-star review classifier |
| Visualization | `matplotlib`, `seaborn`, `wordcloud` | All analytical charts |
| Dashboard | Tableau Public | Executive-facing interactive dashboard |
| Version Control | GitHub | Portfolio + reproducibility |

---

## 📁 Project Structure

```
fintech-sentiment-intelligence/
│
├── data/
│   ├── raw/                          # D1: Raw scraped reviews (4 CSVs)
│   │   ├── cashapp_raw.csv
│   │   ├── venmo_raw.csv
│   │   ├── chime_raw.csv
│   │   └── paypal_raw.csv
│   └── clean/                        # D2: Cleaned, merged dataset
│       ├── all_apps_clean.csv
│       └── negative_reviews.csv
│
├── notebooks/                        # Core analysis (9 sequential notebooks)
│   ├── 01_scraping.ipynb             # Week 1: Data collection
│   ├── 02_cleaning_eda.ipynb         # Week 1: EDA + feature engineering
│   ├── 03_sentiment_analysis.ipynb   # Week 2: VADER sentiment scoring
│   ├── 04_topic_modeling.ipynb       # Week 2: BERTopic complaint themes
│   ├── 05_before_after_analysis.ipynb # Week 2: Pre/Post update analysis
│   ├── 06_competitor_benchmarking.ipynb # Week 2: Cross-app comparison
│   ├── 07_ml_classifier.ipynb        # Week 3: Logistic Regression classifier
│   ├── 08_user_journey_mapping.ipynb  # Week 3: Complaint → journey stage
│   └── 09_financial_impact.ipynb     # Week 3: Revenue impact model
│
├── sql/
│   └── queries.sql                   # D3: 12+ analytical SQL queries
│
├── outputs/
│   ├── charts/                       # All visualization PNGs
│   ├── tables/                       # SQL query result exports
│   └── exports/                      # Final deliverable exports
│
├── dashboard/
│   └── screenshots/                  # Tableau dashboard captures
│
├── docs/
│   └── executive_summary.md          # D13: 1-page executive summary
│
├── .gitignore
├── requirements.txt
└── README.md                         # D14: This file (case study)
```

---

## 📦 Master Deliverables

| # | Deliverable | Format | Location |
|---|-------------|--------|----------|
| D1 | Raw scraped reviews (4 apps) | CSV | `data/raw/` |
| D2 | Cleaned, merged dataset | CSV | `data/clean/` |
| D3 | SQL query file (≥12 queries) | `.sql` | `sql/` |
| D4 | Sentiment analysis results | CSV + notebook | `notebooks/03` |
| D5 | Topic model results (named themes) | CSV + notebook | `notebooks/04` |
| D6 | Before/After update analysis | Notebook + charts | `notebooks/05` |
| D7 | Competitor benchmarking matrix | Heatmap + CSV | `outputs/` |
| D8 | ML-lite classifier (Logistic Regression) | Notebook + charts | `notebooks/07` |
| D9 | User journey complaint map | Chart + CSV | `outputs/` |
| D10 | Financial impact model | Notebook | `notebooks/09` |
| D11 | Recommendation prioritization matrix | Chart | `outputs/` |
| D12 | Interactive dashboard (6 views) | Tableau Public | Public URL |
| D13 | Executive summary (1 page) | PDF/Markdown | `docs/` |
| D14 | README case study | Markdown | GitHub root |

---

## 🗓 Sprint Timeline

| Week | Sprint Focus | Key Outputs |
|------|-------------|-------------|
| **Week 1** | Environment + Data + SQL Foundation | Raw data, clean data, 12 SQL queries, EDA |
| **Week 2** | NLP Core Analysis | Sentiment scores, topic themes, before/after, competitor matrix |
| **Week 3** | ML + User Journey + Financial Impact | Classifier, journey map, revenue model |
| **Week 4** | Dashboard + Documentation + Polish | Tableau dashboard, executive summary, README |

---

## 📈 Status

🟡 **In Progress** — Week 1: Data Foundation

- [x] ~~PBI 1.1 — Environment Setup (Day 1)~~
- [ ] PBI 1.2 — Data Scraping (Day 2)
- [ ] PBI 1.3 — EDA (Day 3)
- [ ] PBI 1.4 — Data Cleaning + Feature Engineering (Day 4)
- [ ] PBI 1.5 — SQL Database + 12 Queries (Day 5)
- [ ] PBI 1.6 — Sprint 1 Review (Day 6-7)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/johnkirima/Fintech-Sentiment-Intelligence-Analysis.git
cd Fintech-Sentiment-Intelligence-Analysis

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Jupyter
jupyter notebook
```

---

## 👤 Author

**John Kirima** | Marketing Analytics Portfolio | 2025–2026

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/john-kirima/)
