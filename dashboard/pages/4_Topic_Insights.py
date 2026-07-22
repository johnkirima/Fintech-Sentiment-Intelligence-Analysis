"""
Topic Insights - What users complain about most
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import load_data

st.set_page_config(page_title="Topic Insights", page_icon="📝", layout="wide")

st.title("📝 Topic Insights & Complaint Analysis")

df = load_data()

# Filters
st.sidebar.header("Filters")
apps = st.sidebar.multiselect("Apps", df['app_name'].unique(), default=df['app_name'].unique())
sentiment_filter = st.sidebar.selectbox("Sentiment Focus", ['All', 'Negative', 'Positive', 'Neutral'])

filtered = df[df['app_name'].isin(apps)]
if sentiment_filter != 'All':
    filtered = filtered[filtered['sentiment'] == sentiment_filter]

# Extract keywords
st.subheader("🔍 Top Keywords in Reviews")

def extract_keywords(text):
    """Extract meaningful keywords"""
    if pd.isna(text):
        return []
    text = str(text).lower()
    words = re.findall(r'\b[a-z]{3,}\b', text)
    stopwords = {'the', 'and', 'this', 'that', 'with', 'for', 'was', 'but', 
                 'have', 'not', 'are', 'you', 'can', 'they', 'been', 'your',
                 'from', 'all', 'use', 'app', 'just', 'like', 'get', 'been',
                 'has', 'had', 'will', 'very', 'really', 'even', 'my'}
    return [w for w in words if w not in stopwords]

all_text = ' '.join(filtered['review_clean'].astype(str))
keywords = extract_keywords(all_text)
keyword_counts = Counter(keywords).most_common(30)

# Bar chart of top keywords
keyword_df = pd.DataFrame(keyword_counts, columns=['Keyword', 'Count'])

fig = px.bar(
    keyword_df,
    x='Count',
    y='Keyword',
    orientation='h',
    color='Count',
    color_continuous_scale='Blues',
    labels={'Count': 'Frequency', 'Keyword': 'Keyword'}
)
fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Crisis keywords
st.subheader("🚨 Crisis Keywords Detection")

crisis_keywords = {
    'Account Access': ['locked', 'frozen', 'suspend', 'block', 'access', 'login'],
    'Money Issues': ['money', 'funds', 'payment', 'transfer', 'missing', 'lost'],
    'Fraud/Security': ['fraud', 'scam', 'hacked', 'stolen', 'unauthorized'],
    'Timing': ['weeks', 'days', 'waiting', 'pending', 'hold', 'delayed'],
    'Support': ['support', 'help', 'customer', 'service', 'contact', 'response']
}

crisis_counts = {}
for category, words in crisis_keywords.items():
    count = sum(filtered['review_clean'].str.lower().str.contains('|'.join(words), na=False))
    crisis_counts[category] = count

crisis_df = pd.DataFrame(list(crisis_counts.items()), columns=['Category', 'Mentions'])
crisis_df = crisis_df.sort_values('Mentions', ascending=False)

fig = px.bar(
    crisis_df,
    x='Category',
    y='Mentions',
    color='Mentions',
    color_continuous_scale='Reds',
    text='Mentions'
)
fig.update_traces(textposition='outside')
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Topic distribution by app
st.markdown("---")
st.subheader("📊 Crisis Topics by App")

topic_by_app = []
for app in filtered['app_name'].unique():
    app_df = filtered[filtered['app_name'] == app]
    for category, words in crisis_keywords.items():
        count = sum(app_df['review_clean'].str.lower().str.contains('|'.join(words), na=False))
        topic_by_app.append({'App': app, 'Topic': category, 'Count': count})

topic_df = pd.DataFrame(topic_by_app)
topic_pivot = topic_df.pivot(index='App', columns='Topic', values='Count').fillna(0)

fig = px.imshow(
    topic_pivot,
    labels=dict(x="Topic", y="App", color="Mentions"),
    x=topic_pivot.columns,
    y=topic_pivot.index,
    color_continuous_scale='Reds',
    text_auto=True,
    aspect='auto'
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Severity by topic
st.markdown("---")
st.subheader("⚠️ Average Severity by Topic")

severity_by_topic = []
for category, words in crisis_keywords.items():
    mask = filtered['review_clean'].str.lower().str.contains('|'.join(words), na=False)
    if mask.sum() > 0:
        avg_sev = filtered[mask]['severity'].mean()
        severity_by_topic.append({'Topic': category, 'Avg Severity': avg_sev})

sev_topic_df = pd.DataFrame(severity_by_topic).sort_values('Avg Severity', ascending=False)

fig = px.bar(
    sev_topic_df,
    x='Topic',
    y='Avg Severity',
    color='Avg Severity',
    color_continuous_scale='RdYlGn_r',
    text='Avg Severity'
)
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Sample reviews by topic
st.markdown("---")
st.subheader("📋 Sample Reviews by Topic")

selected_topic = st.selectbox("Select Topic", list(crisis_keywords.keys()))
topic_words = crisis_keywords[selected_topic]
topic_reviews = filtered[filtered['review_clean'].str.lower().str.contains('|'.join(topic_words), na=False)]

st.write(f"Found **{len(topic_reviews)}** reviews mentioning: {', '.join(topic_words)}")

sample = topic_reviews.sample(min(10, len(topic_reviews)))
for idx, row in sample.iterrows():
    with st.expander(f"{row['app_name']} - {row['rating']}⭐ | Severity {row['severity']}"):
        # Highlight keywords
        review_text = row['review_clean']
        for word in topic_words:
            review_text = re.sub(f'({word})', r'**\1**', review_text, flags=re.IGNORECASE)
        st.markdown(review_text)