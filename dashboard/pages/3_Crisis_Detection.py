"""
Crisis Detection - High severity issues and hidden negatives
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import load_data, COLORS

st.set_page_config(page_title="Crisis Detection", page_icon="🚨", layout="wide")

st.title("🚨 Crisis Detection & Hidden Negatives")

df = load_data()

# Filters
st.sidebar.header("Filters")
apps = st.sidebar.multiselect("Apps", df['app_name'].unique(), default=df['app_name'].unique())
severity_threshold = st.sidebar.slider("Severity Threshold", 1, 5, 4)

filtered = df[df['app_name'].isin(apps)]

# Crisis overview
st.subheader("⚠️ Crisis Overview")

col1, col2, col3 = st.columns(3)

with col1:
    critical = (filtered['severity'] == 5).sum()
    st.metric("🔴 Critical (Severity 5)", f"{critical:,}", delta=f"{critical/len(filtered)*100:.1f}%")

with col2:
    severe = (filtered['severity'] == 4).sum()
    st.metric("🟠 Severe (Severity 4)", f"{severe:,}", delta=f"{severe/len(filtered)*100:.1f}%")

with col3:
    hidden = filtered['is_hidden_negative'].sum()
    st.metric("🔍 Hidden Negatives", f"{hidden:,}", delta=f"{hidden/len(filtered)*100:.1f}%")

st.markdown("---")

# High severity by app
st.subheader(f"📊 High Severity Issues (≥{severity_threshold}) by App")

high_severity = filtered[filtered['severity'] >= severity_threshold]
severity_by_app = high_severity.groupby('app_name').size().sort_values(ascending=False)

fig = px.bar(
    x=severity_by_app.index,
    y=severity_by_app.values,
    labels={'x': 'App', 'y': f'Count (Severity ≥{severity_threshold})'},
    color=severity_by_app.values,
    color_continuous_scale='Reds',
    text=severity_by_app.values
)
fig.update_traces(textposition='outside')
fig.update_layout(showlegend=False, height=400)
st.plotly_chart(fig, use_container_width=True)

# Severity heatmap
st.markdown("---")
st.subheader("🔥 Severity Heatmap by App & Rating")

heatmap_data = filtered.groupby(['app_name', 'rating'])['severity'].mean().unstack(fill_value=0)

fig = px.imshow(
    heatmap_data,
    labels=dict(x="Star Rating", y="App", color="Avg Severity"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    color_continuous_scale='RdYlGn_r',
    text_auto='.2f',
    aspect='auto'
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Hidden negatives analysis
st.markdown("---")
st.subheader("🔍 Hidden Negatives Analysis")

st.info("**Hidden Negatives**: Reviews with positive/neutral sentiment BUT high severity (4-5). These are complaints disguised in polite language.")

hidden_neg = filtered[filtered['is_hidden_negative'] == True]

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Hidden Negatives", f"{len(hidden_neg):,}")
    
    # By app
    hidden_by_app = hidden_neg['app_name'].value_counts()
    fig = px.pie(
        values=hidden_by_app.values,
        names=hidden_by_app.index,
        title="Hidden Negatives by App",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Rating distribution of hidden negatives
    if len(hidden_neg) > 0:
        st.metric("Avg Rating (Hidden Neg)", f"{hidden_neg['rating'].mean():.2f}⭐")
        
        rating_dist = hidden_neg['rating'].value_counts().sort_index()
        fig = px.bar(
            x=rating_dist.index,
            y=rating_dist.values,
            labels={'x': 'Star Rating', 'y': 'Count'},
            title="Rating Distribution of Hidden Negatives",
            color=rating_dist.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Sample critical reviews
st.markdown("---")
st.subheader("📋 Sample Critical Reviews (Severity 5)")

critical_reviews = filtered[filtered['severity'] == 5].sample(min(10, len(filtered[filtered['severity'] == 5])))

for idx, row in critical_reviews.iterrows():
    with st.expander(f"🔴 {row['app_name']} - {row['rating']}⭐ | {row['sentiment']}"):
        st.write(f"**Severity:** {row['severity']}/5")
        st.write(f"**Review:** {row['review_clean']}")

# Sample hidden negatives
st.markdown("---")
st.subheader("📋 Sample Hidden Negatives")

if len(hidden_neg) > 0:
    sample_hidden = hidden_neg.sample(min(10, len(hidden_neg)))
    
    for idx, row in sample_hidden.iterrows():
        with st.expander(f"🔍 {row['app_name']} - {row['rating']}⭐ | {row['sentiment']} (Severity {row['severity']})"):
            st.write(f"**Why it's hidden:** {row['sentiment']} sentiment BUT severity {row['severity']}/5")
            st.write(f"**Review:** {row['review_clean']}")
else:
    st.info("No hidden negatives found with current filters")

# Export
st.markdown("---")
if st.button("📥 Export High Severity Reviews to CSV"):
    high_sev_export = filtered[filtered['severity'] >= severity_threshold][
        ['app_name', 'rating', 'sentiment', 'severity', 'review_clean']
    ]
    csv = high_sev_export.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"high_severity_reviews_threshold_{severity_threshold}.csv",
        mime="text/csv"
    )