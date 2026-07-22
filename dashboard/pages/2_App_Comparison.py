"""
App Comparison - Side-by-side competitive analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import load_data, COLORS

st.set_page_config(page_title="App Comparison", page_icon="🏆", layout="wide")

st.title("🏆 App-to-App Comparison")

df = load_data()

# App selector
st.sidebar.header("Select Apps to Compare")
all_apps = df['app_name'].unique()
selected = st.sidebar.multiselect("Apps", all_apps, default=list(all_apps[:3]))

if len(selected) < 2:
    st.warning("⚠️ Please select at least 2 apps to compare")
    st.stop()

filtered = df[df['app_name'].isin(selected)]

# Comparison metrics
st.subheader("📊 Key Metrics Comparison")

metrics = filtered.groupby('app_name').agg({
    'review_id': 'count',
    'rating': 'mean',
    'severity': 'mean',
    'sentiment': lambda x: (x == 'Negative').mean() * 100,
    'is_hidden_negative': 'sum'
}).round(2)

metrics.columns = ['Total Reviews', 'Avg Rating', 'Avg Severity', 'Negative %', 'Hidden Negatives']

st.dataframe(
    metrics.style.highlight_max(subset=['Total Reviews', 'Avg Rating'], color='lightgreen')
                .highlight_min(subset=['Avg Severity', 'Negative %'], color='lightgreen')
                .format({
                    'Total Reviews': '{:,.0f}',
                    'Avg Rating': '{:.2f}',
                    'Avg Severity': '{:.2f}',
                    'Negative %': '{:.1f}%',
                    'Hidden Negatives': '{:.0f}'
                }),
    use_container_width=True
)

st.markdown("---")

# Side-by-side charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("⭐ Average Rating")
    rating_data = filtered.groupby('app_name')['rating'].mean().sort_values(ascending=False)
    
    fig = px.bar(
        x=rating_data.index,
        y=rating_data.values,
        color=rating_data.values,
        color_continuous_scale='RdYlGn',
        labels={'x': 'App', 'y': 'Average Rating'}
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🚨 Severity Score")
    severity_data = filtered.groupby('app_name')['severity'].mean().sort_values(ascending=False)
    
    fig = px.bar(
        x=severity_data.index,
        y=severity_data.values,
        color=severity_data.values,
        color_continuous_scale='RdYlGn_r',
        labels={'x': 'App', 'y': 'Average Severity'}
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

# Sentiment comparison
st.markdown("---")
st.subheader("🎭 Sentiment Distribution Comparison")

sentiment_comp = filtered.groupby(['app_name', 'sentiment']).size().reset_index(name='count')
sentiment_comp['percentage'] = sentiment_comp.groupby('app_name')['count'].transform(lambda x: x / x.sum() * 100)

fig = px.bar(
    sentiment_comp,
    x='app_name',
    y='percentage',
    color='sentiment',
    barmode='stack',
    color_discrete_map={
        'Positive': COLORS['positive'],
        'Neutral': COLORS['neutral'],
        'Negative': COLORS['negative']
    },
    labels={'app_name': 'App', 'percentage': 'Percentage (%)'},
    text='percentage'
)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Rating distribution heatmap
st.markdown("---")
st.subheader("⭐ Rating Distribution Heatmap")

rating_matrix = filtered.groupby(['app_name', 'rating']).size().unstack(fill_value=0)
rating_pct = rating_matrix.div(rating_matrix.sum(axis=1), axis=0) * 100

fig = px.imshow(
    rating_pct,
    labels=dict(x="Star Rating", y="App", color="Percentage"),
    x=rating_pct.columns,
    y=rating_pct.index,
    color_continuous_scale='YlOrRd',
    text_auto='.1f'
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Hidden negatives comparison
st.markdown("---")
st.subheader("🔍 Hidden Negatives by App")

hidden_counts = filtered.groupby('app_name')['is_hidden_negative'].sum().sort_values(ascending=False)

fig = px.bar(
    x=hidden_counts.index,
    y=hidden_counts.values,
    labels={'x': 'App', 'y': 'Number of Hidden Negatives'},
    color=hidden_counts.values,
    color_continuous_scale='Reds'
)
fig.update_layout(showlegend=False, height=350)
st.plotly_chart(fig, use_container_width=True)

st.info("💡 **Hidden Negatives**: Reviews with positive/neutral sentiment but high severity scores (4-5)")