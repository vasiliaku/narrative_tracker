"""
Nostr Tracker - Monitors Nostr protocol for crypto mentions
Connects directly to multiple reliable Nostr relays
"""

import requests
import json
import re
from collections import Counter
import time

# Multiple stable Nostr relays (not just nostr.band!)
NOSTR_RELAYS_HTTP = [
    "https://relay.nostr.band",
    "https://nostr.wine",
]

# Backup: Use RSS-JSON bridges that are more stable
NOSTR_RSS_BRIDGES = [
    "https://rss.nostr.band/topic/bitcoin",
    "https://rss.nostr.band/topic/crypto",
]

def extract_tickers(text):
    """Extract crypto ticker symbols from text"""
    if not text:
        return []
    
    pattern = r'\$([A-Z]{2,10})\b'
    tickers = re.findall(pattern, text.upper())
    
    pattern2 = r'\b([A-Z]{3,6})\b'
    potential_tickers = re.findall(pattern2, text.upper())
    
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

def try_nostr_relay(relay_url):
    """Try fetching from a specific Nostr relay"""
    try:
        # Use nostr.band's query interface (more stable than raw WebSocket)
        if "nostr.band" in relay_url:
            # Try multiple endpoints
            endpoints = [
                f"{relay_url}/trending/notes",
                f"{relay_url}/search?q=bitcoin",
                f"{relay_url}/search?q=crypto",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        notes = data.get('notes', [])
                        if notes:
                            return notes[:30]  # Return first 30
                except:
                    continue
        
        # Try nostr.wine
        elif "nostr.wine" in relay_url:
            try:
                # nostr.wine has a simple query interface
                response = requests.get(
                    f"{relay_url}/api/search",
                    params={"q": "crypto bitcoin", "limit": 30},
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json().get('results', [])
            except:
                pass
        
        return []
        
    except Exception as e:
        return []

def get_nostr_posts():
    """Fetch posts from multiple Nostr sources"""
    all_posts = []
    
    # Try each relay
    for relay in NOSTR_RELAYS_HTTP:
        try:
            notes = try_nostr_relay(relay)
            
            for note in notes:
                content = note.get('content', '')
                
                # Filter for crypto content
                crypto_terms = ['crypto', 'bitcoin', 'btc', 'lightning', 'sats', 'token', '$']
                if any(term in content.lower() for term in crypto_terms):
                    all_posts.append({
                        'content': content,
                        'pubkey': note.get('pubkey', '')[:8],
                        'created_at': note.get('created_at', 0)
                    })
            
            if all_posts:
                break  # If we got data, no need to try other relays
                
            time.sleep(0.5)  # Rate limiting between relays
            
        except Exception as e:
            continue
    
    # If no posts yet, try RSS bridges as backup
    if not all_posts:
        for bridge_url in NOSTR_RSS_BRIDGES:
            try:
                response = requests.get(bridge_url, timeout=10)
                if response.status_code == 200:
                    # Parse RSS/JSON
                    data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                    if data and 'items' in data:
                        for item in data['items'][:20]:
                            content = item.get('content_text', '') or item.get('title', '')
                            if content:
                                all_posts.append({
                                    'content': content,
                                    'pubkey': 'rss',
                                    'created_at': 0
                                })
                    if all_posts:
                        break
            except:
                continue
    
    # Remove duplicates
    seen = set()
    unique_posts = []
    for post in all_posts:
        content_hash = hash(post['content'][:100])
        if content_hash not in seen:
            seen.add(content_hash)
            unique_posts.append(post)
    
    return unique_posts[:50]  # Limit to 50 posts

def analyze_nostr():
    """Analyze Nostr for crypto mentions"""
    print("\n[NOSTR] Scanning decentralized protocol (multi-relay)...")
    
    posts = get_nostr_posts()
    
    if not posts:
        print("  No posts found from any relay")
        print("  Tip: Nostr relays might be slow. This is normal, will try again next run.")
        return Counter(), []
    
    print(f"  Found {len(posts)} crypto-related posts")
    
    all_tickers = []
    keyword_posts = []
    
    for post in posts:
        content = post['content']
        
        tickers = extract_tickers(content)
        all_tickers.extend(tickers)
        
        keywords = check_keywords(content)
        if keywords:
            keyword_posts.append({
                'content': content[:100],
                'keywords': keywords,
                'tickers': tickers,
                'source': 'nostr'
            })
    
    ticker_counts = Counter(all_tickers)
    
    print(f"  Found {len(ticker_counts)} unique tickers")
    print(f"  Found {len(keyword_posts)} posts with narrative keywords")
    
    return ticker_counts, keyword_posts

if __name__ == "__main__":
    print("Testing Nostr Tracker...")
    tickers, keywords = analyze_nostr()
    
    print("\nTop 10 tickers on Nostr:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: {count} mentions")
    
    if keywords:
        print(f"\nFound {len(keywords)} posts with signals")
