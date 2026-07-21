"""
Sentiment and Severity Analysis Module
Centralized scoring logic with negation handling and fintech crisis detection
"""

import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Initialize VADER
vader = SentimentIntensityAnalyzer()


# ============================================================================
# NEGATION HANDLING
# ============================================================================

def handle_negations(text):
    """
    Preserve the original review text.
    VADER has built-in negation handling, so custom NOT_ rewriting is not needed.
    """
    return text


# ============================================================================
# FINTECH CRISIS LEXICON
# ============================================================================

CRISIS_KEYWORDS = {
    # Account access issues (HIGH severity signals)
    'account_access': [
        'locked', 'freeze', 'frozen', 'suspend', 'restricted', 'block', 'blocked',
        'can\'t access', 'cannot access', 'won\'t load', 'wouldn\'t let',
        'can\'t log', 'can\'t withdraw', 'can\'t transfer'
    ],
    
    # Fraud and security (CRITICAL severity)
    'fraud_security': [
        'hacked', 'fraud', 'scam', 'scammed', 'stolen', 'theft',
        'unauthorized', 'suspicious', 'dispute', 'disputing'
    ],
    
    # Money issues (HIGH severity)
    'money_issues': [
        'lost money', 'missing money', 'disappeared', 'wrong account',
        'never received', 'didn\'t receive', 'charged twice', 'double charged',
        'overdraft', 'declined', 'denied', 'rejected', 'bounced'
    ],
    
    # Timing delays (MODERATE-HIGH severity)
    'timing': [
        'weeks', 'week', 'days waiting', 'still waiting', 'pending',
        'hold', 'held', 'delayed', 'slow', 'forever'
    ],
    
    # Critical life impact (CRITICAL severity booster)
    'life_impact': [
        'rent', 'bills', 'emergency', 'urgent', 'desperate',
        'eviction', 'utilities', 'groceries', 'medication'
    ],
    
    # Informal complaint language (severity booster)
    'informal_negative': [
        'garbage', 'trash', 'awful', 'terrible', 'horrible',
        'worst', 'hate', 'hater', 'sucks', 'useless',
        'joke', 'pathetic', 'ridiculous', 'shady'
    ]
}


def detect_crisis_keywords(text):
    """
    Detect fintech crisis keywords and return category matches.
    Returns dict with categories and their matched keywords.
    """
    text_lower = text.lower()
    matches = {}
    
    for category, keywords in CRISIS_KEYWORDS.items():
        found = []
        for keyword in keywords:
            if keyword in text_lower:
                found.append(keyword)
        if found:
            matches[category] = found
    
    return matches


# ============================================================================
# SENTIMENT SCORING (with negation handling)
# ============================================================================

def get_sentiment(text):
    """
    Classify sentiment using VADER with negation pre-processing.
    
    Returns: 'Positive', 'Negative', or 'Neutral'
    """
    if pd.isna(text) or text.strip() == '':
        return 'Neutral'
    
    # Pre-process negations
    processed_text = handle_negations(text)
    
    # Get VADER scores
    scores = vader.polarity_scores(processed_text)
    compound = scores['compound']
    
    # Classify
    if compound >= 0.05:
        return 'Positive'
    elif compound <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'


# ============================================================================
# SEVERITY SCORING (enhanced with crisis detection)
# ============================================================================

def calculate_severity(text, sentiment, rating=None):
    """
    Calculate severity score (1-5) with crisis keyword boosting.
    
    Parameters:
    - text: review text
    - sentiment: 'Positive', 'Negative', 'Neutral'
    - rating: star rating (1-5), optional but recommended
    
    Returns: int (1-5)
    """
    if pd.isna(text) or text.strip() == '':
        return 1
    
    # Process negations for VADER
    processed_text = handle_negations(text)
    scores = vader.polarity_scores(processed_text)
    compound = scores['compound']
    
    # Detect crisis keywords
    crisis_matches = detect_crisis_keywords(text)
    
    # Base severity from VADER intensity
    if sentiment == 'Negative':
        abs_compound = abs(compound)
        
        # Map compound score to base severity
        if abs_compound >= 0.75:
            base_severity = 4
        elif abs_compound >= 0.50:
            base_severity = 3
        elif abs_compound >= 0.25:
            base_severity = 2
        else:
            base_severity = 1
    
    elif sentiment == 'Positive':
        # Positive reviews are low severity by default
        base_severity = 1
        
        # But check for hidden negatives (positive words masking complaints)
        if crisis_matches:
            base_severity = 3  # Bump up if crisis keywords present
    
    else:  # Neutral
        base_severity = 2
    
    # Apply crisis keyword boosters
    severity_boost = 0
    
    # Critical severity boosters
    if 'fraud_security' in crisis_matches:
        severity_boost += 2  # Fraud is always critical
    
    if 'life_impact' in crisis_matches:
        severity_boost += 2  # Bills/rent issues are critical
    
    # High severity boosters
    if 'account_access' in crisis_matches:
        severity_boost += 1
    
    if 'money_issues' in crisis_matches:
        severity_boost += 1
    
    # Moderate boosters
    if 'timing' in crisis_matches:
        severity_boost += 1
    
    if 'informal_negative' in crisis_matches:
        # Words like "garbage", "shady" indicate strong frustration
        severity_boost += 1
    
    # Calculate final severity
    final_severity = base_severity + severity_boost
    
    # Rating-based fallback (if we have star rating)
    if rating is not None and rating <= 2 and final_severity < 3:
        # 1-2 star reviews should be at least moderate severity
        final_severity = max(final_severity, 3)
    
    # Clamp to 1-5 range
    final_severity = max(1, min(5, final_severity))
    
    return final_severity


SEVERITY_MAP = {
    1: 'Low',
    2: 'Moderate',
    3: 'High',
    4: 'Severe',
    5: 'Critical'
}


def get_severity_label(severity_score):
    """Map numeric severity to label"""
    return SEVERITY_MAP.get(severity_score, 'Unknown')


# ============================================================================
# HIDDEN NEGATIVE DETECTION
# ============================================================================

def is_hidden_negative(sentiment, severity_score, rating=None):
    """
    Detect hidden negatives: reviews that appear positive/neutral 
    but contain serious complaints.
    
    Returns: bool
    """
    # Positive/neutral sentiment but high severity
    if sentiment in ['Positive', 'Neutral'] and severity_score >= 4:
        return True
    
    # High rating but critical severity (rating-text mismatch)
    if rating is not None and rating >= 4 and severity_score >= 4:
        return True
    
    return False


# ============================================================================
# FULL ANALYSIS PIPELINE
# ============================================================================

def analyze_review(text, rating=None):
    """
    Complete analysis pipeline for a single review.
    
    Parameters:
    - text: review text (str)
    - rating: star rating 1-5 (int, optional)
    
    Returns: dict with all analysis results
    """
    sentiment = get_sentiment(text)
    severity_score = calculate_severity(text, sentiment, rating)
    severity_label = get_severity_label(severity_score)
    hidden_negative = is_hidden_negative(sentiment, severity_score, rating)
    
    return {
        'sentiment': sentiment,
        'severity_score': severity_score,
        'severity_label': severity_label,
        'is_hidden_negative': hidden_negative
    }


def analyze_dataframe(df, text_col='review_text', rating_col='rating'):
    """
    Apply analysis to entire DataFrame.
    
    Parameters:
    - df: pandas DataFrame
    - text_col: name of column containing review text
    - rating_col: name of column containing star rating (optional)
    
    Returns: DataFrame with analysis columns added
    """
    df = df.copy()
    
    # Check if rating column exists
    has_rating = rating_col in df.columns
    
    # Apply analysis
    if has_rating:
        results = df.apply(
            lambda row: analyze_review(row[text_col], row[rating_col]), 
            axis=1
        )
    else:
        results = df[text_col].apply(lambda text: analyze_review(text))
    
    # Unpack results into separate columns
    df['vader_sentiment'] = results.apply(lambda x: x['sentiment'])
    df['severity_score'] = results.apply(lambda x: x['severity_score'])
    df['severity_label'] = results.apply(lambda x: x['severity_label'])
    df['is_hidden_negative'] = results.apply(lambda x: x['is_hidden_negative'])
    
    return df


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Test examples
    test_cases = [
        ("not good at all", 1),
        ("can't access my money for weeks", 1),
        ("Great app but my account got hacked", 5),
        ("Love it!", 5),
        ("garbage app, shady practices", 1),
    ]
    
    print("Testing improved sentiment engine:\n")
    print("=" * 80)
    
    for text, rating in test_cases:
        result = analyze_review(text, rating)
        print(f"\nText: {text}")
        print(f"Rating: {rating}★")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Severity: {result['severity_score']} ({result['severity_label']})")
        print(f"Hidden Negative: {result['is_hidden_negative']}")
        print("-" * 80)