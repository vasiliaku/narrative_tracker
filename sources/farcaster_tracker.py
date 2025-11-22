"""
Farcaster Tracker - Monitors Farcaster protocol for crypto mentions
Farcaster is a crypto-native social network with high-quality discussions
"""

import requests
import re
from collections import Counter

# Farcaster API endpoint (using Neynar's free API)
FARCASTER_API = "https://api.neynar.com/v2/farcaster/feed/trending"

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
        'alpha', 'early', 'announcement', 'drop'
    ]
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def get_farcaster_casts():
    """Fetch trending casts from Farcaster"""
    try:
        print("  Fetching from Farcaster...")
        
        # Using public Farcaster hub API
        # Alternative: Use searchcaster.xyz API
        url = "https://searchcaster.xyz/api/search?text=crypto&count=50"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  Warning: Farcaster API returned {response.status_code}")
            # Try alternative approach - just search for common crypto terms
            return get_farcaster_alternative()
        
        data = response.json()
        casts = data.get('casts', [])
        
        posts = []
        for cast in casts[:50]:
            text = cast.get('body', {}).get('data', {}).get('text', '')
            if text:
                posts.append({
                    'text': text,
                    'username': cast.get('body', {}).get('username', 'unknown'),
                    'timestamp': cast.get('body', {}).get('publishedAt', 0)
                })
        
        return posts
    
    except Exception as e:
        print(f"  Error fetching from Farcaster: {str(e)[:100]}")
        return []

def get_farcaster_alternative():
    """Alternative method using Warpcast public API"""
    try:
        # Warpcast is the main Farcaster client
        # We can search trending casts
        searches = ['airdrop', 'presale', 'token launch', '$']
        all_posts = []
        
        for term in searches:
            try:
                url = f"https://searchcaster.xyz/api/search?text={term}&count=20"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    casts = data.get('casts', [])
                    
                    for cast in casts:
                        text = cast.get('body', {}).get('data', {}).get('text', '')
                        if text:
                            all_posts.append({
                                'text': text,
                                'username': cast.get('body', {}).get('username', 'unknown'),
                                'timestamp': cast.get('body', {}).get('publishedAt', 0)
                            })
            except:
                continue
        
        return all_posts[:50]  # Return top 50
    
    except Exception as e:
        print(f"  Alternative fetch also failed: {str(e)[:50]}")
        return []

def analyze_farcaster():
    """Analyze Farcaster for crypto mentions"""
    print("\n[FARCASTER] Scanning crypto-native social network...")
    
    posts = get_farcaster_casts()
    
    if not posts:
        print("  No posts found or API unavailable")
        return Counter(), []
    
    print(f"  Found {len(posts)} recent casts")
    
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
    print("Testing Farcaster Tracker...")
    tickers, keywords = analyze_farcaster()
    
    print("\nTop 10 tickers on Farcaster:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: {count} mentions")
    
    if keywords:
        print(f"\nFound {len(keywords)} casts with signals")
