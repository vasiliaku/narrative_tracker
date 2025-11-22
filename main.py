import requests
import re
import json
import os
from collections import Counter
from datetime import datetime

# Major coins to exclude from results
MAJORS_TO_EXCLUDE = [
    'BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX', 
    'DOT', 'MATIC', 'LINK', 'UNI', 'LTC', 'ATOM', 'XLM', 'ALGO',
    'VET', 'FIL', 'NEAR', 'ARB'
]

HISTORY_FILE = 'crypto_tracking_history.json'

def get_reddit_posts(subreddit, limit=100):
    """Fetch recent posts from a subreddit"""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        headers = {'User-Agent': 'CryptoNarrativeTracker/1.0'}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        posts = []
        for post in data['data']['children']:
            post_data = post['data']
            posts.append({
                'title': post_data['title'],
                'selftext': post_data.get('selftext', ''),
                'score': post_data['score'],
                'num_comments': post_data['num_comments'],
                'created': post_data['created_utc']
            })
        
        return posts
    
    except Exception as e:
        print(f"Error fetching from r/{subreddit}: {e}")
        return []

def extract_tickers(text):
    """Extract crypto ticker symbols from text"""
    pattern = r'\$([A-Z]{2,10})\b'
    tickers = re.findall(pattern, text.upper())
    
    pattern2 = r'\b([A-Z]{3,6})\b'
    potential_tickers = re.findall(pattern2, text.upper())
    
    common_cryptos = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC']
    tickers.extend([t for t in potential_tickers if t in common_cryptos])
    
    return tickers

def analyze_subreddit(subreddit, limit=100):
    """Analyze a subreddit for crypto mentions"""
    print(f"Scanning r/{subreddit}...")
    
    posts = get_reddit_posts(subreddit, limit)
    
    if not posts:
        return Counter()
    
    all_tickers = []
    
    for post in posts:
        text = post['title'] + ' ' + post['selftext']
        tickers = extract_tickers(text)
        all_tickers.extend(tickers)
    
    return Counter(all_tickers)

def load_history():
    """Load historical tracking data"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_to_history(ticker_data):
    """Save current scan to history"""
    history = load_history()
    
    # Add timestamp and data
    entry = {
        'timestamp': datetime.now().isoformat(),
        'tickers': ticker_data
    }
    
    history.append(entry)
    
    # Keep only last 100 scans
    if len(history) > 100:
        history = history[-100:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def calculate_trends(current_mentions):
    """Calculate which tickers are trending up"""
    history = load_history()
    
    if len(history) < 2:
        return {}
    
    # Get previous scan
    previous = history[-2]['tickers'] if len(history) >= 2 else {}
    
    trends = {}
    for ticker, current_count in current_mentions.items():
        previous_count = previous.get(ticker, 0)
        change = current_count - previous_count
        
        if previous_count > 0:
            percent_change = ((change / previous_count) * 100)
        else:
            percent_change = 100 if current_count > 0 else 0
        
        trends[ticker] = {
            'change': change,
            'percent': percent_change,
            'previous': previous_count
        }
    
    return trends

def main():
    """Main function to track crypto narratives"""
    print("=" * 70)
    print("CRYPTO NARRATIVE TRACKER - Emerging Coins Edition")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    subreddits = [
        'CryptoCurrency',
        'CryptoMoonShots', 
        'SatoshiStreetBets',
        'altcoin'
    ]
    
    total_mentions = Counter()
    
    for subreddit in subreddits:
        ticker_counts = analyze_subreddit(subreddit, limit=50)
        total_mentions.update(ticker_counts)
    
    # Filter out major coins
    filtered_mentions = {k: v for k, v in total_mentions.items() 
                        if k not in MAJORS_TO_EXCLUDE}
    
    # Calculate trends
    trends = calculate_trends(filtered_mentions)
    
    # Save to history
    save_to_history(filtered_mentions)
    
    # Display results
    print("\n" + "=" * 70)
    print("TOP 20 EMERGING CRYPTO TICKERS (Majors Excluded)")
    print("=" * 70)
    
    if filtered_mentions:
        print(f"\n{'Rank':<6} {'Ticker':<10} {'Mentions':<10} {'Trend':<20} {'Bar'}")
        print("-" * 70)
        
        for rank, (ticker, count) in enumerate(Counter(filtered_mentions).most_common(20), 1):
            bar = "=" * min(count, 40)
            
            # Show trend if available
            trend_str = ""
            if ticker in trends:
                change = trends[ticker]['change']
                prev = trends[ticker]['previous']
                if change > 0:
                    trend_str = f"UP +{change} ({prev}->{count})"
                elif change < 0:
                    trend_str = f"DOWN {change} ({prev}->{count})"
                else:
                    trend_str = f"SAME ({count})"
            else:
                trend_str = "NEW"
            
            print(f"{rank:<6} ${ticker:<9} {count:<10} {trend_str:<20} {bar}")
    else:
        print("\nNo tickers found. Try running again in a moment.")
    
    print("\n" + "=" * 70)
    print(f"Total emerging tickers found: {len(filtered_mentions)}")
    print(f"Total mentions tracked: {sum(filtered_mentions.values())}")
    
    # Show biggest movers
    if trends:
        print("\nBIGGEST MOVERS (vs last scan):")
        print("-" * 70)
        sorted_trends = sorted(trends.items(), 
                              key=lambda x: x[1]['change'], 
                              reverse=True)[:5]
        
        for ticker, trend_data in sorted_trends:
            if trend_data['change'] > 0:
                print(f"  ${ticker}: +{trend_data['change']} mentions "
                      f"({trend_data['previous']} -> {filtered_mentions[ticker]})")
    
    print("\n" + "=" * 70)
    history_count = len(load_history())
    print(f"Historical scans saved: {history_count}")
    print("TIP: Run this regularly to spot emerging narratives early!")
    print("=" * 70)

if __name__ == "__main__":
    main()
