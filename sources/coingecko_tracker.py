"""
CoinGecko Tracker - Monitors trending coins and new listings
This is the validation layer - if it's trending here, the narrative is heating up!
"""

import requests
from collections import Counter

COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_trending_coins():
    """Fetch trending coins from CoinGecko"""
    try:
        print("  Fetching trending coins...")
        
        url = f"{COINGECKO_API}/search/trending"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"  Warning: CoinGecko returned {response.status_code}")
            return []
        
        data = response.json()
        coins = data.get('coins', [])
        
        trending = []
        for item in coins:
            coin = item.get('item', {})
            trending.append({
                'symbol': coin.get('symbol', '').upper(),
                'name': coin.get('name', ''),
                'rank': coin.get('market_cap_rank', 999),
                'score': coin.get('score', 0)
            })
        
        return trending
    
    except Exception as e:
        print(f"  Error fetching trending: {str(e)[:100]}")
        return []

def get_new_coins():
    """Fetch recently added coins"""
    try:
        print("  Fetching new listings...")
        
        # Get coins sorted by recently added
        url = f"{COINGECKO_API}/coins/list?include_platform=false"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return []
        
        # CoinGecko doesn't have a "new coins" endpoint in free tier
        # So we'll just return empty for now
        # The trending coins are more valuable anyway
        return []
    
    except Exception as e:
        print(f"  Error fetching new coins: {str(e)[:50]}")
        return []

def get_top_gainers():
    """Fetch top gaining coins (price movers)"""
    try:
        print("  Fetching price movers...")
        
        # Get market data for top coins
        url = f"{COINGECKO_API}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'percent_change_24h_desc',
            'per_page': 20,
            'page': 1,
            'sparkline': False
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        gainers = []
        for coin in data:
            change = coin.get('price_change_percentage_24h', 0)
            if change and change > 10:  # Only coins up >10%
                gainers.append({
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name', ''),
                    'change': round(change, 2),
                    'volume': coin.get('total_volume', 0)
                })
        
        return gainers
    
    except Exception as e:
        print(f"  Error fetching gainers: {str(e)[:50]}")
        return []

def analyze_coingecko():
    """Analyze CoinGecko data for trending narratives"""
    print("\n[COINGECKO] Checking trending coins & price movers...")
    
    # Get trending coins
    trending = get_trending_coins()
    
    # Get top gainers
    gainers = get_top_gainers()
    
    # Combine tickers
    all_tickers = []
    
    # Add trending coins (weight them more)
    for coin in trending:
        symbol = coin['symbol']
        # Add 3x for trending (they're hot!)
        all_tickers.extend([symbol] * 3)
    
    # Add gainers
    for coin in gainers:
        symbol = coin['symbol']
        # Add 2x for price gainers
        all_tickers.extend([symbol] * 2)
    
    ticker_counts = Counter(all_tickers)
    
    # Create keyword posts for trending signals
    keyword_posts = []
    
    for coin in trending[:5]:  # Top 5 trending
        keyword_posts.append({
            'content': f"{coin['name']} (${coin['symbol']}) is trending on CoinGecko",
            'keywords': ['trending', 'hot'],
            'tickers': [coin['symbol']],
            'source': 'coingecko',
            'rank': coin['rank']
        })
    
    for coin in gainers[:5]:  # Top 5 gainers
        if coin['change'] > 20:  # Only big moves
            keyword_posts.append({
                'content': f"{coin['name']} (${coin['symbol']}) up {coin['change']}% in 24h",
                'keywords': ['pump', 'gainers'],
                'tickers': [coin['symbol']],
                'source': 'coingecko',
                'change': coin['change']
            })
    
    print(f"  Found {len(trending)} trending coins")
    print(f"  Found {len(gainers)} significant price movers")
    print(f"  Total unique tickers: {len(ticker_counts)}")
    
    return ticker_counts, keyword_posts

if __name__ == "__main__":
    print("Testing CoinGecko Tracker...")
    tickers, keywords = analyze_coingecko()
    
    print("\nTop tickers on CoinGecko:")
    for ticker, count in tickers.most_common(10):
        print(f"  ${ticker}: weight {count}")
    
    if keywords:
        print(f"\nHot signals: {len(keywords)}")
        for signal in keywords[:3]:
            print(f"  - {signal['content']}")
