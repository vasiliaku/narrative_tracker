"""
Farcaster Tracker - Monitors Farcaster protocol for crypto mentions
Using ONLY free Neynar endpoints + local filtering
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
    """
    Fetch casts from Farcaster using ONLY free Neynar endpoints
    Then filter locally (no paid /filter endpoint!)
    """
    try:
        print("  Fetching from Farcaster via Neynar (free endpoints only)...")
        
        all_casts = []
        
        # Try 'for-you' feed (this is FREE)
        try:
            url = f"{NEYNAR_BASE_URL}/feed"
            params = {
                'feed_type': 'for-you',
                'limit': 100  # Get more to filter from
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
                print(f"    Got {len(casts)} casts from for-you feed")
            elif response.status_code == 402:
                print(f"    Warning: for-you feed hit payment wall (skip)")
            else:
                print(f"    Warning: for-you feed returned {response.status_code}")
                
        except Exception as e:
            print(f"    Error with for-you feed: {str(e)[:50]}")
        
        # If for-you didn't work, try getting recent casts (also FREE)
        if not all_casts:
            try:
                url = f"{NEYNAR_BASE_URL}/casts"
                params = {
                    'limit': 50
                }
                headers = {
                    'api_key': NEYNAR_API_KEY,
                    'accept': 'application/json'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    all_casts = data.get('casts', [])
                    print(f"    Got {len(all_casts)} recent casts")
                    
            except Exception as e:
                print(f"    Error with recent casts: {str(e)[:50]}")
        
        # Now filter locally for crypto content (this avoids paid /filter endpoint!)
        crypto_posts = []
        crypto_keywords = ['crypto', 'bitcoin', 'btc', 'eth', 'token', 'coin', 'defi', 'web3', '$', 
                          'airdrop', 'presale', 'launch', 'mint']
        
        for cast in all_casts[:100]:
            text = cast.get('text', '')
            
            # Check if crypto-related
            if any(kw in text.lower() for kw in crypto_keywords):
                author = cast.get('author', {})
                username = author.get('username', 'unknown')
                
                crypto_posts.append({
                    'text': text,
                    'username': username,
                    'timestamp': cast.get('timestamp', '')
                })
        
        return crypto_posts
    
    except Exception as e:
        print(f"  Error fetching from Farcaster: {str(e)[:100]}")
        return []

def analyze_farcaster():
    """Analyze Farcaster for crypto mentions"""
    print("\n[FARCASTER] Scanning crypto-native social network...")
    
    posts = get_farcaster_feed()
    
    if not posts:
        print("  No posts found - Neynar free tier might be exhausted")
        print("  Tip: Free tier resets daily. Will work again tomorrow!")
        return Counter(), []
    
    print(f"  Found {len(posts)} crypto-related casts (filtered locally)")
    
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
    print("Testing Farcaster Tracker with free endpoints...")
    tickers, keywords = analyze_farcaster()
    
    print("\nTop 10 tickers on Farcaster:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: {count} mentions")
    
    if keywords:
        print(f"\nFound {len(keywords)} casts with signals")
        for kw in keywords[:3]:
            print(f"  - {kw['content'][:80]}...")
