"""
Reddit Tracker - Monitors crypto subreddits via RSS feeds
This is where community narratives form!
"""

import requests
import re
import xml.etree.ElementTree as ET
from collections import Counter
from html import unescape

def get_reddit_rss(subreddit):
    """Fetch posts from Reddit RSS feed"""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/new/.rss"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        posts = []
        for entry in root.findall('atom:entry', ns):
            title_elem = entry.find('atom:title', ns)
            content_elem = entry.find('atom:content', ns)
            
            title = ""
            content = ""
            
            if title_elem is not None and title_elem.text:
                title = unescape(title_elem.text)
            
            if content_elem is not None and content_elem.text:
                content_text = re.sub('<[^<]+?>', '', content_elem.text)
                content = unescape(content_text)
            
            if title or content:
                posts.append({
                    'title': title,
                    'content': content
                })
        
        return posts
    
    except Exception as e:
        return []

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

def analyze_reddit():
    """Analyze crypto subreddits for mentions"""
    print("\n[REDDIT] Scanning crypto subreddits via RSS...")
    
    subreddits = [
        'CryptoCurrency',
        'CryptoMoonShots',
        'SatoshiStreetBets',
        'altcoin'
    ]
    
    all_tickers = []
    keyword_posts = []
    
    for subreddit in subreddits:
        print(f"  Scanning r/{subreddit}...")
        posts = get_reddit_rss(subreddit)
        
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
    
    ticker_counts = Counter(all_tickers)
    
    print(f"  Found {len(ticker_counts)} unique tickers")
    print(f"  Found {len(keyword_posts)} posts with narrative keywords")
    
    return ticker_counts, keyword_posts

if __name__ == "__main__":
    print("Testing Reddit Tracker...")
    tickers, keywords = analyze_reddit()
    
    print("\nTop 10 tickers on Reddit:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: {count} mentions")
