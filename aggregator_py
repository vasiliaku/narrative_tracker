"""
Aggregator - Combines data from all sources into unified insights
This is the brain of the operation!
"""

import json
import os
from collections import Counter
from datetime import datetime

# Major coins to exclude
MAJORS_TO_EXCLUDE = [
    'BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX',
    'DOT', 'MATIC', 'LINK', 'UNI', 'LTC', 'ATOM', 'XLM', 'ALGO',
    'VET', 'FIL', 'NEAR', 'APT', 'ARB', 'OP', 'HBAR', 'INJ'
]

HISTORY_FILE = 'crypto_tracking_history.json'

def aggregate_tickers(source_data):
    """
    Combine ticker mentions from all sources
    source_data = {
        'reddit': Counter({'VOOZ': 3, 'HUNT': 2}),
        'nostr': Counter({'VOOZ': 1, 'ALPHA': 2}),
        ...
    }
    """
    # Weight sources differently (earlier sources get more weight)
    weights = {
        'nostr': 3,      # Earliest signal
        'telegram': 3,   # Project announcements
        'farcaster': 2,  # Crypto-native
        'reddit': 1,     # Community validation
        'coingecko': 2   # Market validation
    }
    
    combined = Counter()
    source_breakdown = {}
    
    for source, tickers in source_data.items():
        weight = weights.get(source, 1)
        source_breakdown[source] = dict(tickers)
        
        for ticker, count in tickers.items():
            # Skip major coins
            if ticker in MAJORS_TO_EXCLUDE:
                continue
            
            # Apply weight
            combined[ticker] += count * weight
    
    return combined, source_breakdown

def aggregate_keywords(keyword_posts):
    """
    Combine keyword signals from all sources
    """
    # Group by ticker
    ticker_signals = {}
    
    for post in keyword_posts:
        for ticker in post.get('tickers', []):
            if ticker in MAJORS_TO_EXCLUDE:
                continue
            
            if ticker not in ticker_signals:
                ticker_signals[ticker] = {
                    'keywords': [],
                    'sources': [],
                    'posts': []
                }
            
            ticker_signals[ticker]['keywords'].extend(post.get('keywords', []))
            ticker_signals[ticker]['sources'].append(post.get('source', 'unknown'))
            ticker_signals[ticker]['posts'].append(post.get('content', '')[:100])
    
    return ticker_signals

def calculate_narrative_score(ticker, combined_count, source_breakdown, signals):
    """
    Calculate a narrative score for each ticker
    Higher score = stronger narrative
    """
    score = 0
    
    # Base score from mentions
    score += combined_count
    
    # Bonus for being mentioned across multiple sources
    sources_count = len([s for s in source_breakdown.values() if ticker in s])
    score += sources_count * 5
    
    # Bonus for having keyword signals
    if ticker in signals:
        signal_data = signals[ticker]
        score += len(signal_data['keywords']) * 2
        
        # Extra bonus for high-value keywords
        high_value = ['presale', 'airdrop', 'launch', 'listing']
        for kw in signal_data['keywords']:
            if kw in high_value:
                score += 3
    
    return score

def detect_cross_platform_trends(source_breakdown):
    """
    Find tickers that appear on multiple platforms
    These are the strongest signals!
    """
    cross_platform = {}
    
    # Find tickers appearing on 2+ platforms
    all_tickers = set()
    for tickers in source_breakdown.values():
        all_tickers.update(tickers.keys())
    
    for ticker in all_tickers:
        if ticker in MAJORS_TO_EXCLUDE:
            continue
        
        platforms = []
        total_mentions = 0
        
        for source, tickers in source_breakdown.items():
            if ticker in tickers:
                platforms.append(source)
                total_mentions += tickers[ticker]
        
        if len(platforms) >= 2:  # Appears on 2+ platforms
            cross_platform[ticker] = {
                'platforms': platforms,
                'mentions': total_mentions,
                'cross_platform_score': len(platforms) * total_mentions
            }
    
    return cross_platform

def generate_insights(combined, source_breakdown, signals):
    """
    Generate actionable insights from aggregated data
    """
    insights = []
    
    # Find cross-platform trends
    cross_platform = detect_cross_platform_trends(source_breakdown)
    
    if cross_platform:
        insights.append({
            'type': 'cross_platform_alert',
            'message': f"🔥 {len(cross_platform)} tickers detected across multiple platforms!",
            'tickers': list(cross_platform.keys())[:5]
        })
    
    # Find early signals (mentioned on Nostr/Telegram but not mainstream yet)
    if 'nostr' in source_breakdown or 'telegram' in source_breakdown:
        early_sources = ['nostr', 'telegram']
        mainstream_sources = ['reddit', 'coingecko']
        
        early_tickers = set()
        for source in early_sources:
            if source in source_breakdown:
                early_tickers.update(source_breakdown[source].keys())
        
        mainstream_tickers = set()
        for source in mainstream_sources:
            if source in source_breakdown:
                mainstream_tickers.update(source_breakdown[source].keys())
        
        only_early = early_tickers - mainstream_tickers - set(MAJORS_TO_EXCLUDE)
        
        if only_early:
            insights.append({
                'type': 'genesis_alert',
                'message': f"🌱 {len(only_early)} tokens detected in genesis phase (not mainstream yet)!",
                'tickers': list(only_early)[:5]
            })
    
    # Find tokens with strong keyword signals
    high_signal_tickers = []
    for ticker, signal_data in signals.items():
        if len(signal_data['keywords']) >= 3:  # 3+ different keywords
            high_signal_tickers.append(ticker)
    
    if high_signal_tickers:
        insights.append({
            'type': 'keyword_alert',
            'message': f"⚡ {len(high_signal_tickers)} tokens with strong narrative signals!",
            'tickers': high_signal_tickers[:5]
        })
    
    return insights

def save_aggregated_data(combined, source_breakdown, signals, insights):
    """
    Save aggregated data to history file
    """
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'tickers': dict(combined),
        'source_breakdown': source_breakdown,
        'signals': {k: {
            'keyword_count': len(v['keywords']),
            'sources': list(set(v['sources'])),
            'sample_posts': v['posts'][:3]
        } for k, v in signals.items()},
        'insights': insights
    }
    
    history.append(entry)
    
    # Keep last 100 entries
    if len(history) > 100:
        history = history[-100:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"\n✅ Data saved to {HISTORY_FILE}")

def aggregate_all_sources(source_data, all_keyword_posts):
    """
    Main aggregation function
    """
    print("\n" + "=" * 70)
    print("AGGREGATING DATA FROM ALL SOURCES")
    print("=" * 70)
    
    # Combine tickers
    combined, source_breakdown = aggregate_tickers(source_data)
    
    # Process keyword signals
    signals = aggregate_keywords(all_keyword_posts)
    
    # Calculate narrative scores
    scored_tickers = []
    for ticker, count in combined.most_common():
        score = calculate_narrative_score(ticker, count, source_breakdown, signals)
        scored_tickers.append({
            'ticker': ticker,
            'weighted_mentions': count,
            'narrative_score': score,
            'sources': [s for s in source_breakdown if ticker in source_breakdown[s]]
        })
    
    # Generate insights
    insights = generate_insights(combined, source_breakdown, signals)
    
    # Save data
    save_aggregated_data(combined, source_breakdown, signals, insights)
    
    return scored_tickers, signals, insights

if __name__ == "__main__":
    print("Aggregator module loaded")
