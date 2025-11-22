import requests
import re
import json
import os
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from html import unescape

# Major coins to exclude from results
MAJORS_TO_EXCLUDE = [
    'BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX', 
    'DOT', 'MATIC', 'LINK', 'UNI', 'LTC', 'ATOM', 'XLM', 'ALGO',
    'VET', 'FIL', 'NEAR', 'APT', 'ARB', 'OP', 'HBAR', 'INJ'
]

# Keywords to track for early narrative signals
NARRATIVE_KEYWORDS = [
    'airdrop', 'presale', 'launch', 'launched', 'launching',
    'new coin', 'new token', 'fair launch', 'stealth launch',
    'ido', 'ico', 'listing', 'whitelist', 'mint', 'minting'
]

HISTORY_FILE = 'crypto_tracking_history.json'

def get_reddit_rss(subreddit):
    """Fetch posts from Reddit RSS feed"""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/new/.rss"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  Warning: Got status {response.status_code} from r/{subreddit}")
            return []
        
        # Parse RSS XML - Reddit uses Atom format
        root = ET.fromstring(response.content)
        
        # Define namespace for Atom feeds
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        posts = []
        # Find all entry elements
        for entry in root.findall('atom:entry', ns):
            title_elem = entry.find('atom:title', ns)
            content_elem = entry.find('atom:content', ns)
            
            title = ""
            content = ""
            
            if title_elem is not None and title_elem.text:
                title = unescape(title_elem.text)
            
            if content_elem is not None and content_elem.text:
                # Remove HTML tags from content
                content_text = re.sub('<[^<]+?>', '', content_elem.text)
                content = unescape(content_text)
            
            if title or content:
                posts.append({
                    'title': title,
                    'content': content
                })
        
        return posts
    
    except Exception as e:
        print(f"  Error parsing RSS from r/{subreddit}: {str(e)[:100]}")
        return []

def extract_tickers(text):
    """Extract crypto ticker symbols from text"""
    # Match $TICKER pattern
    pattern = r'\$([A-Z]{2,10})\b'
    tickers = re.findall(pattern, text.upper())
    
    # Also catch standalone tickers (3-6 letters, all caps)
    pattern2 = r'\b([A-Z]{3,6})\b'
    potential_tickers = re.findall(pattern2, text.upper())
    
    # Include common cryptos even without $
    common_cryptos = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC']
    tickers.extend([t for t in potential_tickers if t in common_cryptos])
    
    return list(set(tickers))  # Remove duplicates

def check_keywords(text):
    """Check if text contains narrative keywords"""
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in NARRATIVE_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def analyze_subreddit(subreddit):
    """Analyze a subreddit RSS feed for crypto mentions"""
    print(f"Scanning r/{subreddit} via RSS...")
    
    posts = get_reddit_rss(subreddit)
    
    if not posts:
        return Counter(), []
    
    print(f"  Found {len(posts)} recent posts")
    
    all_tickers = []
    keyword_posts = []
    
    for post in posts:
        # Combine title and content
        text = post['title'] + ' ' + post['content']
        tickers = extract_tickers(text)
        all_tickers.extend(tickers)
        
        # Check for narrative keywords
        keywords = check_keywords(text)
        if keywords:
            keyword_posts.append({
                'title': post['title'][:100],  # Truncate long titles
                'keywords': keywords,
                'tickers': tickers
            })
    
    return Counter(all_tickers), keyword_posts

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
    print("CRYPTO NARRATIVE TRACKER - RSS Edition (Genesis Mode)")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nUsing Reddit RSS feeds to catch early narratives...")
    
    subreddits = [
        'CryptoCurrency',
        'CryptoMoonShots', 
        'SatoshiStreetBets',
        'altcoin'
    ]
    
    total_mentions = Counter()
    all_keyword_posts = []
    
    print("\n" + "-" * 70)
    for subreddit in subreddits:
        ticker_counts, keyword_posts = analyze_subreddit(subreddit)
        total_mentions.update(ticker_counts)
        all_keyword_posts.extend(keyword_posts)
    
    print("-" * 70)
    
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
        print("\nNo tickers found. This could mean:")
        print("  - RSS feeds are empty right now")
        print("  - Reddit might be blocking RSS access")
        print("  - Try running again in a few minutes")
    
    print("\n" + "=" * 70)
    print(f"Total emerging tickers found: {len(filtered_mentions)}")
    print(f"Total mentions tracked: {sum(filtered_mentions.values())}")
    
    # Show narrative keyword alerts
    if all_keyword_posts:
        print("\n" + "=" * 70)
        print("NARRATIVE ALERTS - Posts with key signals!")
        print("=" * 70)
        
        # Group by keyword
        keyword_groups = {}
        for post in all_keyword_posts:
            for kw in post['keywords']:
                if kw not in keyword_groups:
                    keyword_groups[kw] = []
                keyword_groups[kw].append(post)
        
        for keyword, posts in sorted(keyword_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"\n'{keyword.upper()}' mentioned in {len(posts)} posts:")
            for post in posts[:3]:  # Show top 3 posts per keyword
                tickers_str = ', '.join(['$' + t for t in post['tickers'][:3]]) if post['tickers'] else 'no tickers'
                print(f"  - {post['title']}")
                print(f"    Tickers: {tickers_str}")
    
    # Show biggest movers
    if trends:
        print("\n" + "=" * 70)
        print("BIGGEST MOVERS (vs last scan):")
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
    print("TIP: Run this every 1-2 hours to catch narratives in genesis mode!")
    print("=" * 70)

if __name__ == "__main__":
    main()
