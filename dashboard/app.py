"""
Fintech Sentiment Intelligence Dashboard
Main landing page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, get_app_stats, COLORS

# Page config
st.set_page_config(
    page_title="Fintech Sentiment Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">💰 Fintech Sentiment Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Analysis of 25,000+ Customer Reviews</div>', unsafe_allow_html=True)

# Load data
with st.spinner("Loading data..."):
    df = load_data()

if df is None:
    st.error("Failed to load data. Please check data files.")
    st.stop()

# Sidebar filters
st.sidebar.header("🎯 Filters")
selected_apps = st.sidebar.multiselect(
    "Select Apps",
    options=df['app_name'].unique(),
    default=df['app_name'].unique()
)

# Filter data
filtered_df = df[df['app_name'].isin(selected_apps)]

# Top-level KPIs
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Reviews", f"{len(filtered_df):,}")

with col2:
    neg_pct = (filtered_df['sentiment'] == 'Negative').mean() * 100
    st.metric("Negative Sentiment", f"{neg_pct:.1f}%")

with col3:
    avg_rating = filtered_df['rating'].mean()
    st.metric("Avg Rating", f"{avg_rating:.2f}⭐")

with col4:
    high_severity = (filtered_df['severity'] >= 4).sum()
    st.metric("High Severity Issues", f"{high_severity:,}")

with col5:
    hidden_neg = filtered_df['is_hidden_negative'].sum()
    st.metric("Hidden Negatives", f"{hidden_neg:,}")

st.markdown("---")

# Two-column layout
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Sentiment Distribution by App")
    
    sentiment_counts = filtered_df.groupby(['app_name', 'sentiment']).size().reset_index(name='count')
    
    fig = px.bar(
        sentiment_counts,
        x='app_name',
        y='count',
        color='sentiment',
        color_discrete_map={
            'Positive': COLORS['positive'],
            'Neutral': COLORS['neutral'],
            'Negative': COLORS['negative']
        },
        barmode='stack',
        labels={'app_name': 'App', 'count': 'Number of Reviews'},
        height=400
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Number of Reviews",
        legend_title="Sentiment",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🎯 Average Severity Score by App")
    
    severity_by_app = filtered_df.groupby('app_name')['severity'].mean().sort_values(ascending=False).reset_index()
    
    fig = px.bar(
        severity_by_app,
        x='app_name',
        y='severity',
        color='severity',
        color_continuous_scale=['#2ecc71', '#f39c12', '#e74c3c'],
        labels={'app_name': 'App', 'severity': 'Avg Severity (1-5)'},
        height=400
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Average Severity Score",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# App comparison table
st.markdown("---")
st.subheader("📈 App Performance Summary")

stats = get_app_stats(filtered_df)
st.dataframe(
    stats.style.background_gradient(cmap='RdYlGn_r', subset=['Negative %'])
                .background_gradient(cmap='RdYlGn_r', subset=['Avg Severity'])
                .background_gradient(cmap='YlGn', subset=['Avg Rating'])
                .format({
                    'Total Reviews': '{:,.0f}',
                    'Avg Rating': '{:.2f}',
                    'Negative %': '{:.1f}%',
                    'Avg Severity': '{:.2f}',
                    'Hidden Negatives': '{:.0f}'
                }),
    use_container_width=True
)

# Project info
st.markdown("---")
st.markdown("""
### 🎯 About This Dashboard

This dashboard analyzes **25,000+ customer reviews** from 5 major fintech apps using advanced NLP and sentiment analysis.

**Key Features:**
- 🤖 **AI Sentiment Detection** - Identifies positive, neutral, and negative reviews
- ⚠️ **Severity Scoring** - Rates issue urgency on a 1-5 scale
- 🔍 **Hidden Negative Detection** - Finds complaints disguised as positive reviews
- 📊 **Competitive Benchmarking** - Compare apps side-by-side

**Navigate** using the sidebar to explore:
- **Overview** - High-level trends and KPIs
- **App Comparison** - Detailed competitive analysis
- **Crisis Detection** - Critical issues and hidden negatives
- **Topic Insights** - What customers complain about most

---
*Built by John Kirima | [GitHub](https://github.com/johnkirima/Fintech-Sentiment-Intelligence-Analysis)*
""")