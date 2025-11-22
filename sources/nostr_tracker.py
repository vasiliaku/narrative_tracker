"""
Nostr Tracker - Monitors Nostr protocol for crypto mentions
Nostr is a decentralized social protocol where many crypto devs post early alpha
"""

import requests
import json
import re
from collections import Counter

# Popular Nostr relays
NOSTR_RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.nostr.band",
    "wss://nos.lol"
]

# We'll use nostr.band API for easier access
NOSTR_API = "https://api.nostr.band/v0/trending/notes"

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
    common_cryptos = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE']
    tickers.extend([t for t in potential_tickers if t in common_cryptos])
    
    return list(set(tickers))

def check_keywords(text):
    """Check for narrative keywords"""
    if not text:
        return []
    
    keywords = [
        'airdrop', 'presale', 'launch', 'launched', 'launching',
        'new coin', 'new token', 'alpha', 'early', 'mint',
        'testnet', 'mainnet', 'announcement', 'release'
    ]
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def get_nostr_posts():
    """Fetch trending posts from Nostr"""
    try:
        print("  Fetching from Nostr (decentralized protocol)...")
        
        # Using nostr.band API for simplicity
        response = requests.get(NOSTR_API, timeout=15)
        
        if response.status_code != 200:
            print(f"  Warning: Nostr API returned {response.status_code}")
            return []
        
        data = response.json()
        
        posts = []
        notes = data.get('notes', [])
        
        for note in notes[:50]:  # Get top 50 trending notes
            content = note.get('content', '')
            
            # Filter for crypto-related content
            crypto_terms = ['crypto', 'bitcoin', 'btc', 'eth', 'token', 'coin', 'defi', 'web3', '$']
            if any(term in content.lower() for term in crypto_terms):
                posts.append({
                    'content': content,
                    'pubkey': note.get('pubkey', '')[:8],  # First 8 chars of public key
                    'created_at': note.get('created_at', 0)
                })
        
        return posts
    
    except Exception as e:
        print(f"  Error fetching from Nostr: {str(e)[:100]}")
        return []

def analyze_nostr():
    """Analyze Nostr for crypto mentions"""
    print("\n[NOSTR] Scanning decentralized social protocol...")
    
    posts = get_nostr_posts()
    
    if not posts:
        print("  No posts found or API unavailable")
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
