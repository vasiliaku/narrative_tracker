"""
Multi-Source Crypto Narrative Tracker
Aggregates data from: Nostr, Telegram, Farcaster, Reddit, CoinGecko
"""

import sys
import os
from datetime import datetime

# Add sources directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'sources'))

# Import all trackers
try:
    from sources import reddit_tracker
    from sources import nostr_tracker
    from sources import telegram_tracker
    from sources import farcaster_tracker
    from sources import coingecko_tracker
except ImportError:
    # Fallback if running from different directory
    import reddit_tracker
    import nostr_tracker
    import telegram_tracker
    import farcaster_tracker
    import coingecko_tracker

import aggregator

def print_header():
    """Print fancy header"""
    print("\n" + "=" * 70)
    print("🚀 MULTI-SOURCE CRYPTO NARRATIVE TRACKER")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nSources: Nostr | Telegram | Farcaster | Reddit | CoinGecko")
    print("Mode: Genesis Detection + Cross-Platform Validation")
    print("=" * 70)

def run_all_trackers():
    """Run all source trackers and collect data"""
    source_data = {}
    all_keyword_posts = []
    
    # Reddit
    try:
        reddit_tickers, reddit_keywords = reddit_tracker.analyze_reddit()
        source_data['reddit'] = reddit_tickers
        all_keyword_posts.extend(reddit_keywords)
    except Exception as e:
        print(f"❌ Reddit tracker failed: {e}")
        source_data['reddit'] = {}
    
    # Nostr
    try:
        nostr_tickers, nostr_keywords = nostr_tracker.analyze_nostr()
        source_data['nostr'] = nostr_tickers
        all_keyword_posts.extend(nostr_keywords)
    except Exception as e:
        print(f"❌ Nostr tracker failed: {e}")
        source_data['nostr'] = {}
    
    # Telegram
    try:
        telegram_tickers, telegram_keywords = telegram_tracker.analyze_telegram()
        source_data['telegram'] = telegram_tickers
        all_keyword_posts.extend(telegram_keywords)
    except Exception as e:
        print(f"❌ Telegram tracker failed: {e}")
        source_data['telegram'] = {}
    
    # Farcaster
    try:
        farcaster_tickers, farcaster_keywords = farcaster_tracker.analyze_farcaster()
        source_data['farcaster'] = farcaster_tickers
        all_keyword_posts.extend(farcaster_keywords)
    except Exception as e:
        print(f"❌ Farcaster tracker failed: {e}")
        source_data['farcaster'] = {}
    
    # CoinGecko
    try:
        coingecko_tickers, coingecko_keywords = coingecko_tracker.analyze_coingecko()
        source_data['coingecko'] = coingecko_tickers
        all_keyword_posts.extend(coingecko_keywords)
    except Exception as e:
        print(f"❌ CoinGecko tracker failed: {e}")
        source_data['coingecko'] = {}
    
    return source_data, all_keyword_posts

def display_results(scored_tickers, signals, insights):
    """Display formatted results"""
    print("\n" + "=" * 70)
    print("📊 TOP 20 EMERGING NARRATIVES")
    print("=" * 70)
    
    if not scored_tickers:
        print("\n  No data found. Check your internet connection.")
        return
    
    print(f"\n{'Rank':<6} {'Ticker':<10} {'Score':<8} {'Sources':<30} {'Signals'}")
    print("-" * 70)
    
    for i, item in enumerate(scored_tickers[:20], 1):
        ticker = item['ticker']
        score = item['narrative_score']
        sources = ', '.join(item['sources'])
        
        # Get signal keywords
        signal_kws = []
        if ticker in signals:
            signal_kws = list(set(signals[ticker]['keywords']))[:3]
        
        signals_str = ', '.join(signal_kws) if signal_kws else '-'
        
        print(f"{i:<6} ${ticker:<9} {score:<8} {sources:<30} {signals_str}")
    
    # Display insights
    if insights:
        print("\n" + "=" * 70)
        print("🎯 KEY INSIGHTS")
        print("=" * 70)
        
        for insight in insights:
            print(f"\n{insight['message']}")
            if 'tickers' in insight:
                tickers_str = ', '.join([f'${t}' for t in insight['tickers']])
                print(f"  → {tickers_str}")
    
    # Display narrative keyword alerts
    print("\n" + "=" * 70)
    print("🔔 NARRATIVE ALERTS")
    print("=" * 70)
    
    keyword_summary = {}
    for ticker, signal_data in signals.items():
        for kw in signal_data['keywords']:
            if kw not in keyword_summary:
                keyword_summary[kw] = []
            keyword_summary[kw].append(ticker)
    
    # Sort by frequency
    sorted_keywords = sorted(keyword_summary.items(), key=lambda x: len(x[1]), reverse=True)
    
    for keyword, tickers in sorted_keywords[:10]:
        tickers_str = ', '.join([f'${t}' for t in tickers[:5]])
        print(f"\n'{keyword.upper()}' - {len(tickers)} mentions")
        print(f"  Tickers: {tickers_str}")
    
    print("\n" + "=" * 70)
    print("✅ Scan Complete!")
    print("=" * 70)
    print(f"\nTotal tickers tracked: {len(scored_tickers)}")
    print(f"Cross-platform signals: {len([i for i in insights if i['type'] == 'cross_platform_alert'])}")
    print(f"Genesis phase detections: {len([i for i in insights if i['type'] == 'genesis_alert'])}")
    print("\n💡 TIP: Run this every 2-4 hours to track narrative evolution!")
    print("=" * 70 + "\n")

def main():
    """Main execution"""
    print_header()
    
    # Run all trackers
    print("\n🔍 Scanning all sources...")
    source_data, all_keyword_posts = run_all_trackers()
    
    # Aggregate data
    scored_tickers, signals, insights = aggregator.aggregate_all_sources(
        source_data, 
        all_keyword_posts
    )
    
    # Display results
    display_results(scored_tickers, signals, insights)

if __name__ == "__main__":
    main()
