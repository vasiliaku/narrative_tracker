"""
Telegram Tracker - Monitors public Telegram channels for crypto mentions
This is where most projects make their first announcements!
"""

import re
from collections import Counter

# For now, we'll use a simpler approach without requiring Telegram API
# We can scrape public channel previews or use Telegram's t.me preview API

def extract_tickers(text):
    """Extract crypto ticker symbols from text"""
    if not text:
        return []
    
    pattern = r'\$([A-Z]{2,10})\b'
    tickers = re.findall(pattern, text.upper())
    
    pattern2 = r'\b([A-Z]{3,6})\b'
    potential_tickers = re.findall(pattern2, text.upper())
    
    common_cryptos = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE']
    tickers.extend([t for t in potential_tickers if t in common_cryptos])
    
    return list(set(tickers))

def check_keywords(text):
    """Check for narrative keywords"""
    if not text:
        return []
    
    keywords = [
        'airdrop', 'presale', 'launch', 'launched', 'launching',
        'new coin', 'new token', 'announcement', 'listing',
        'ido', 'ico', 'whitelist', 'mint', 'fair launch'
    ]
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def analyze_telegram():
    """
    Analyze Telegram channels for crypto mentions
    
    NOTE: To fully enable this, you need Telegram API credentials:
    1. Go to https://my.telegram.org/apps
    2. Create an app to get api_id and api_hash
    3. Add them to a config file
    
    For now, this is a placeholder that returns sample data.
    We'll implement the full version once you have credentials!
    """
    print("\n[TELEGRAM] Monitoring public channels...")
    print("  ⚠️  Telegram tracking requires API credentials")
    print("  To enable: Visit https://my.telegram.org/apps")
    print("  For now, using mock data for testing...")
    
    # Mock data - replace this with actual Telegram scraping
    # once you have API credentials
    mock_posts = [
        {
            'text': 'New token $ALPHA launching tomorrow! Presale live!',
            'channel': 'crypto_gems',
        },
        {
            'text': 'Airdrop alert for $BETA holders!',
            'channel': 'airdrop_alerts',
        }
    ]
    
    all_tickers = []
    keyword_posts = []
    
    for post in mock_posts:
        text = post['text']
        
        tickers = extract_tickers(text)
        all_tickers.extend(tickers)
        
        keywords = check_keywords(text)
        if keywords:
            keyword_posts.append({
                'content': text[:100],
                'keywords': keywords,
                'tickers': tickers,
                'source': 'telegram'
            })
    
    ticker_counts = Counter(all_tickers)
    
    print(f"  ℹ️  Telegram integration ready for activation")
    print(f"  Found {len(ticker_counts)} tickers (mock data)")
    
    return ticker_counts, keyword_posts

# Advanced implementation (for when you have API credentials)
"""
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

def analyze_telegram_full(api_id, api_hash, phone):
    # Popular crypto Telegram channels to monitor
    channels = [
        'cryptogemss',
        'airdropalert', 
        'CryptoMoonShots',
        'binance_announcements'
    ]
    
    client = TelegramClient('session', api_id, api_hash)
    client.start(phone)
    
    all_tickers = []
    keyword_posts = []
    
    for channel in channels:
        try:
            messages = client(GetHistoryRequest(
                peer=channel,
                limit=50,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))
            
            for message in messages.messages:
                if message.message:
                    tickers = extract_tickers(message.message)
                    all_tickers.extend(tickers)
                    
                    keywords = check_keywords(message.message)
                    if keywords:
                        keyword_posts.append({
                            'content': message.message[:100],
                            'keywords': keywords,
                            'tickers': tickers,
                            'source': 'telegram'
                        })
        except Exception as e:
            print(f"  Error reading {channel}: {e}")
    
    return Counter(all_tickers), keyword_posts
"""

if __name__ == "__main__":
    print("Testing Telegram Tracker...")
    tickers, keywords = analyze_telegram()
    
    print("\nTickers found:")
    for ticker, count in tickers.most_common():
        print(f"  ${ticker}: {count} mentions")
