"""
Reddit Tracker - Monitors crypto subreddits
Using .json endpoints with better headers to avoid blocks
"""

import requests
import re
from collections import Counter
import time

def extract_tickers(text):
    """Extract crypto ticker symbols from text"""
    if not text:
        return []
    
    pattern = r'\$([A-Z]{2,10})\b'
    tickers = re.findall(pattern, text.upper())
    
    pattern2 = r'\b([A-Z]{3,6})\b'
    potential_tickers = re.findall(pattern2, text.upper())
    
    common_cryptos = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC']
    tickers.extend([t for t in potential_tickers if t in common_cryptos])
    
    return list(set(tickers))

def check_keywords(text):
    """Check for narrative keywords"""
    if not text:
        return []
    
    keywords = [
        'airdrop', 'presale', 'launch', 'launched', 'launching',
        'new coin', 'new token', 'fair launch', 'stealth launch',
        'ido', 'ico', 'listing', 'whitelist', 'mint', 'minting'
    ]
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def get_reddit_json(subreddit):
    """
    Fetch posts from Reddit using .json endpoint
    This works without OAuth and avoids API restrictions
    """
    try:
        # Use .json endpoint (not RSS, not API)
        url = f"https://www.reddit.com/r/{subreddit}/new.json"
        
        # Better headers to avoid bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        params = {
            'limit': 50,  # Get 50 posts
            'raw_json': 1  # Avoid HTML entities
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 429:
            print(f"    Rate limited on r/{subreddit} - will skip this run")
            return []
        
        if response.status_code != 200:
            print(f"    Warning: r/{subreddit} returned {response.status_code}")
            return []
        
        data = response.json()
        
        posts = []
        children = data.get('data', {}).get('children', [])
        
        for child in children:
            post_data = child.get('data', {})
            
            title = post_data.get('title', '')
            selftext = post_data.get('selftext', '')
            
            if title or selftext:
                posts.append({
                    'title': title,
                    'content': selftext
                })
        
        return posts
    
    except Exception as e:
        print(f"    Error fetching r/{subreddit}: {str(e)[:50]}")
        return []

def analyze_reddit():
    """Analyze crypto subreddits for mentions"""
    print("\n[REDDIT] Scanning crypto subreddits (.json method)...")
    
    subreddits = [
        'CryptoCurrency',
        'CryptoMoonShots',
        'SatoshiStreetBets',
        'altcoin'
    ]
    
    all_tickers = []
    keyword_posts = []
    total_posts = 0
    
    for subreddit in subreddits:
        print(f"  Scanning r/{subreddit}...")
        posts = get_reddit_json(subreddit)
        total_posts += len(posts)
        
        for post in posts:
            text = post['title'] + ' ' + post['content']
            
            tickers = extract_tickers(text)
            all_tickers.extend(tickers)
            
            keywords = check_keywords(text)
            if keywords:
                keyword_posts.append({
                    'content': post['title'][:100],
                    'keywords': keywords,
                    'tickers': tickers,
                    'source': 'reddit',
                    'subreddit': subreddit
                })
        
        # Rate limiting between subreddits
        time.sleep(2)
    
    ticker_counts = Counter(all_tickers)
    
    print(f"  Found {total_posts} total posts across all subs")
    print(f"  Found {len(ticker_counts)} unique tickers")
    print(f"  Found {len(keyword_posts)} posts with narrative keywords")
    
    return ticker_counts, keyword_posts

if __name__ == "__main__":
    print("Testing Reddit Tracker with .json method...")
    tickers, keywords = analyze_reddit()
    
    print("\nTop 10 tickers on Reddit:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: {count} mentions")
