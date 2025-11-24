"""
Nostr Tracker - Monitors Nostr protocol for crypto mentions
Connects directly to multiple Nostr relays for reliable data
"""

import requests
import json
import re
from collections import Counter
import time

# Popular Nostr relays to connect to
NOSTR_RELAYS = [
    "https://relay.nostr.band",
    "https://nostr.wine",
    "https://relay.damus.io"
]

# Using nostr.band API as fallback (doesn't require WebSocket)
NOSTR_BAND_API = "https://api.nostr.band/v0"

def extract_tickers(text):
    """Extract crypto ticker symbols from text"""
    if not text:
        return []
    
    # Match $TICKER pattern
    pattern = r'\$([A-Z]{2,10})\b'
    tickers = re.findall(pattern, text.upper())
    
    # Also catch standalone tickers
    pattern2 = r'\b([A-Z]{3,6})\b'
    potential_tickers = re.findall(pattern2, text.upper())
    
    # Include common cryptos
    common_cryptos = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'SATS', 'ORDI']
    tickers.extend([t for t in potential_tickers if t in common_cryptos])
    
    return list(set(tickers))

def check_keywords(text):
    """Check for narrative keywords"""
    if not text:
        return []
    
    keywords = [
        'airdrop', 'presale', 'launch', 'launched', 'launching',
        'new coin', 'new token', 'alpha', 'early', 'mint',
        'testnet', 'mainnet', 'announcement', 'release', 'drop'
    ]
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def get_nostr_trending():
    """Fetch trending notes from Nostr.band API"""
    try:
        url = f"{NOSTR_BAND_API}/trending/notes"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            print(f"  Warning: Nostr.band returned {response.status_code}")
            return []
        
        data = response.json()
        notes = data.get('notes', [])
        
        posts = []
        for note in notes[:50]:  # Get top 50 trending
            content = note.get('content', '')
            
            # Filter for crypto-related content
            crypto_terms = ['crypto', 'bitcoin', 'btc', 'lightning', 'sats', 'token', 'coin', '$']
            if any(term in content.lower() for term in crypto_terms):
                posts.append({
                    'content': content,
                    'pubkey': note.get('pubkey', '')[:8],
                    'created_at': note.get('created_at', 0)
                })
        
        return posts
        
    except Exception as e:
        print(f"  Error with Nostr.band: {str(e)[:50]}")
        return []

def get_nostr_search(keywords):
    """Search Nostr for specific keywords"""
    try:
        # Use nostr.band search endpoint
        posts = []
        
        for keyword in keywords[:3]:  # Search top 3 keywords to avoid rate limits
            try:
                url = f"{NOSTR_BAND_API}/search"
                params = {
                    'q': keyword,
                    'kind': 1,  # Text notes
                    'limit': 20
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    notes = data.get('notes', [])
                    
                    for note in notes:
                        content = note.get('content', '')
                        if content:
                            posts.append({
                                'content': content,
                                'pubkey': note.get('pubkey', '')[:8],
                                'created_at': note.get('created_at', 0)
                            })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  Error searching '{keyword}': {str(e)[:30]}")
                continue
        
        return posts
        
    except Exception as e:
        print(f"  Error with Nostr search: {str(e)[:50]}")
        return []

def get_nostr_posts():
    """Fetch posts from Nostr using multiple methods"""
    all_posts = []
    
    # Method 1: Get trending posts
    trending = get_nostr_trending()
    all_posts.extend(trending)
    
    # Method 2: Search for specific crypto keywords
    search_keywords = ['airdrop', 'presale', 'bitcoin alpha']
    search_results = get_nostr_search(search_keywords)
    all_posts.extend(search_results)
    
    # Remove duplicates based on content
    seen = set()
    unique_posts = []
    for post in all_posts:
        content_hash = hash(post['content'][:100])
        if content_hash not in seen:
            seen.add(content_hash)
            unique_posts.append(post)
    
    return unique_posts

def analyze_nostr():
    """Analyze Nostr for crypto mentions"""
    print("\n[NOSTR] Scanning decentralized social protocol...")
    
    posts = get_nostr_posts()
    
    if not posts:
        print("  No posts found or API unavailable")
        print("  Tip: Nostr.band might be rate limiting. Try again in a few minutes.")
        return Counter(), []
    
    print(f"  Found {len(posts)} crypto-related posts")
    
    all_tickers = []
    keyword_posts = []
    
    for post in posts:
        content = post['content']
        
        # Extract tickers
        tickers = extract_tickers(content)
        all_tickers.extend(tickers)
        
        # Check for keywords
        keywords = check_keywords(content)
        if keywords:
            keyword_posts.append({
                'content': content[:100],  # First 100 chars
                'keywords': keywords,
                'tickers': tickers,
                'source': 'nostr'
            })
    
    ticker_counts = Counter(all_tickers)
    
    print(f"  Found {len(ticker_counts)} unique tickers")
    print(f"  Found {len(keyword_posts)} posts with narrative keywords")
    
    return ticker_counts, keyword_posts

if __name__ == "__main__":
    # Test the tracker
    print("Testing Nostr Tracker...")
    tickers, keywords = analyze_nostr()
    
    print("\nTop 10 tickers on Nostr:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: {count} mentions")
    
    if keywords:
        print(f"\nFound {len(keywords)} posts with signals")
        for kw in keywords[:3]:
            print(f"  - {kw['content'][:80]}...")
