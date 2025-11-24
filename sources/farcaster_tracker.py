"""
Farcaster Tracker - Monitors Farcaster protocol for crypto mentions
Using Neynar API v2 for reliable data access
"""

import requests
import re
from collections import Counter

# Neynar API Configuration
NEYNAR_API_KEY = "74397244-51B9-43EA-A3B8-3324B79B03A0"
NEYNAR_BASE_URL = "https://api.neynar.com/v2/farcaster"

def extract_tickers(text):
    """Extract crypto ticker symbols from text"""
    if not text:
        return []
    
    pattern = r'\$([A-Z]{2,10})\b'
    tickers = re.findall(pattern, text.upper())
    
    pattern2 = r'\b([A-Z]{3,6})\b'
    potential_tickers = re.findall(pattern2, text.upper())
    
    common_cryptos = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'BASE', 'WARP']
    tickers.extend([t for t in potential_tickers if t in common_cryptos])
    
    return list(set(tickers))

def check_keywords(text):
    """Check for narrative keywords"""
    if not text:
        return []
    
    keywords = [
        'airdrop', 'presale', 'launch', 'launched', 'launching',
        'new coin', 'new token', 'mint', 'minting',
        'alpha', 'early', 'announcement', 'drop', 'testnet', 'mainnet'
    ]
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def get_farcaster_feed():
    """Fetch recent casts from Farcaster using Neynar API v2"""
    try:
        print("  Fetching from Farcaster via Neynar API...")
        
        # Try multiple feed types for better coverage
        feed_types = ['filter', 'following']
        all_casts = []
        
        for feed_type in feed_types:
            try:
                url = f"{NEYNAR_BASE_URL}/feed"
                
                params = {
                    'feed_type': feed_type,
                    'limit': 50
                }
                
                headers = {
                    'api_key': NEYNAR_API_KEY,
                    'accept': 'application/json'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    casts = data.get('casts', [])
                    all_casts.extend(casts)
                    print(f"    Got {len(casts)} casts from {feed_type} feed")
                elif response.status_code == 401:
                    print(f"  Warning: API key issue (401) - check your Neynar key")
                    break
                else:
                    print(f"  Warning: {feed_type} feed returned {response.status_code}")
                    
            except Exception as e:
                print(f"  Error with {feed_type} feed: {str(e)[:50]}")
                continue
        
        # If no casts from feeds, try trending casts
        if not all_casts:
            try:
                url = f"{NEYNAR_BASE_URL}/feed/trending"
                headers = {
                    'api_key': NEYNAR_API_KEY,
                    'accept': 'application/json'
                }
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    all_casts = data.get('casts', [])
                    print(f"    Got {len(all_casts)} trending casts")
            except Exception as e:
                print(f"  Error with trending: {str(e)[:50]}")
        
        # Parse casts
        posts = []
        for cast in all_casts[:100]:  # Process up to 100 casts
            text = cast.get('text', '')
            author = cast.get('author', {})
            username = author.get('username', 'unknown')
            
            # Filter for crypto-related content
            crypto_terms = ['crypto', 'bitcoin', 'btc', 'eth', 'token', 'coin', 'defi', 'web3', '$', 'airdrop', 'presale']
            if any(term in text.lower() for term in crypto_terms):
                posts.append({
                    'text': text,
                    'username': username,
                    'timestamp': cast.get('timestamp', '')
                })
        
        return posts
    
    except Exception as e:
        print(f"  Error fetching from Farcaster: {str(e)[:100]}")
        return []

def analyze_farcaster():
    """Analyze Farcaster for crypto mentions"""
    print("\n[FARCASTER] Scanning crypto-native social network...")
    
    posts = get_farcaster_feed()
    
    if not posts:
        print("  No posts found or API unavailable")
        print("  Tip: Check if your Neynar API key is valid at https://neynar.com")
        return Counter(), []
    
    print(f"  Found {len(posts)} crypto-related casts")
    
    all_tickers = []
    keyword_posts = []
    
    for post in posts:
        text = post['text']
        
        # Extract tickers
        tickers = extract_tickers(text)
        all_tickers.extend(tickers)
        
        # Check for keywords
        keywords = check_keywords(text)
        if keywords:
            keyword_posts.append({
                'content': text[:100],
                'keywords': keywords,
                'tickers': tickers,
                'source': 'farcaster',
                'username': post.get('username', 'unknown')
            })
    
    ticker_counts = Counter(all_tickers)
    
    print(f"  Found {len(ticker_counts)} unique tickers")
    print(f"  Found {len(keyword_posts)} casts with narrative keywords")
    
    return ticker_counts, keyword_posts

if __name__ == "__main__":
    print("Testing Farcaster Tracker with Neynar API...")
    tickers, keywords = analyze_farcaster()
    
    print("\nTop 10 tickers on Farcaster:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: {count} mentions")
    
    if keywords:
        print(f"\nFound {len(keywords)} casts with signals")
        for kw in keywords[:3]:
            print(f"  - {kw['content'][:80]}...")
