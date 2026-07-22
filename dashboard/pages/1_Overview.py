"""
Shared utility functions for the dashboard
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.analysis import analyze_dataframe

# Cache data loading for performance
import streamlit as st

@st.cache_data
def load_data():
    """Load and prepare the full dataset with analysis"""
    data_path = Path(__file__).parent.parent / "data" / "clean" / "all_apps_clean.csv"
    
    if not data_path.exists():
        st.error(f"Data file not found: {data_path}")
        return None
    
    df = pd.read_csv(data_path)
    
    # Run sentiment + severity analysis
    df = analyze_dataframe(df, text_col='review_clean', rating_col='rating')
    
    # Rename columns for consistency
    df = df.rename(columns={
        'vader_sentiment': 'sentiment',
        'severity_score': 'severity'
    })
    
    return df


@st.cache_data
def load_labels():
    """Load human-labeled validation data"""
    labels_path = Path(__file__).parent.parent / "data" / "labels" / "labels.csv"
    
    if not labels_path.exists():
        return None
    
    return pd.read_csv(labels_path)


def get_app_stats(df):
    """Calculate key stats by app"""
    stats = df.groupby('app_name').agg({
        'review_id': 'count',
        'rating': 'mean',
        'sentiment': lambda x: (x == 'Negative').mean() * 100,
        'severity': 'mean',
        'is_hidden_negative': 'sum'
    }).round(2)
    
    stats.columns = ['Total Reviews', 'Avg Rating', 'Negative %', 'Avg Severity', 'Hidden Negatives']
    stats = stats.sort_values('Negative %', ascending=False)
    
    return stats


def filter_data(df, apps=None, sentiments=None, severity_range=None, rating_range=None):
    """Apply filters to dataframe"""
    filtered = df.copy()
    
    if apps:
        filtered = filtered[filtered['app_name'].isin(apps)]
    
    if sentiments:
        filtered = filtered[filtered['sentiment'].isin(sentiments)]
    
    if severity_range:
        filtered = filtered[
            (filtered['severity'] >= severity_range[0]) & 
            (filtered['severity'] <= severity_range[1])
        ]
    
    if rating_range:
        filtered = filtered[
            (filtered['rating'] >= rating_range[0]) & 
            (filtered['rating'] <= rating_range[1])
        ]
    
    return filtered


# Color schemes for consistent branding
COLORS = {
    'negative': '#e74c3c',
    'neutral': '#95a5a6',
    'positive': '#2ecc71',
    'severity_low': '#3498db',
    'severity_high': '#e74c3c',
    'apps': {
        'Chime': '#00a868',
        'Cash App': '#00d632',
        'Venmo': '#3d95ce',
        'PayPal': '#0070ba',
        'Zelle': '#6d1ed4'
    }
}


def get_sentiment_color(sentiment):
    """Return color for sentiment"""
    return COLORS.get(sentiment.lower(), COLORS['neutral'])