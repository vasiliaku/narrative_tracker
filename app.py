from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime
from collections import Counter

app = Flask(__name__)

HISTORY_FILE = 'crypto_tracking_history.json'


def load_latest_data():
    """Load the most recent tracking data"""
    if not os.path.exists(HISTORY_FILE):
        return None

    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            if history:
                return history[-1], len(history)
    except:
        pass
    return None, 0


def calculate_trends(history):
    """Calculate trends from history"""
    if len(history) < 2:
        return {}

    current = history[-1]['tickers']
    previous = history[-2]['tickers']

    trends = {}
    for ticker, count in current.items():
        prev_count = previous.get(ticker, 0)
        change = count - prev_count
        trends[ticker] = {
            'change': change,
            'previous': prev_count,
            'is_new': prev_count == 0,
            'percent': ((change / prev_count) * 100) if prev_count > 0 else 100
        }

    return trends


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Crypto Narrative Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="120">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 25px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }

        .header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3em;
            font-weight: 800;
            margin-bottom: 10px;
        }

        .header .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 15px;
        }

        .status-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .last-update {
            color: #888;
            font-size: 0.9em;
            margin-top: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .stat-label {
            color: #666;
            font-size: 0.95em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 25px;
            margin-bottom: 25px;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }

        .card h2 {
            color: #1e293b;
            margin-bottom: 25px;
            font-size: 1.8em;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .ticker-row {
            display: flex;
            align-items: center;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
            background: #f8fafc;
        }

        .ticker-row:hover {
            background: #e0e7ff;
            transform: translateX(5px);
        }

        .ticker-rank {
            font-size: 1.2em;
            font-weight: 700;
            color: #94a3b8;
            width: 40px;
        }

        .ticker-symbol {
            font-size: 1.3em;
            font-weight: 700;
            color: #667eea;
            width: 100px;
        }

        .ticker-mentions {
            font-size: 1.1em;
            font-weight: 600;
            color: #1e293b;
            width: 80px;
        }

        .ticker-trend {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .trend-badge {
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 0.85em;
            font-weight: 700;
            white-space: nowrap;
        }

        .trend-new {
            background: #fef3c7;
            color: #92400e;
        }

        .trend-up {
            background: #d1fae5;
            color: #065f46;
        }

        .trend-down {
            background: #fee2e2;
            color: #991b1b;
        }

        .progress-bar {
            flex: 1;
            height: 8px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            transition: width 0.5s ease;
        }

        .hot-signals {
            grid-column: span 1;
        }

        .signal-item {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border-left: 4px solid #f59e0b;
        }

        .signal-keyword {
            font-size: 1.1em;
            font-weight: 700;
            color: #92400e;
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .signal-count {
            color: #78350f;
            font-size: 0.9em;
            margin-bottom: 10px;
        }

        .signal-tickers {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .signal-ticker {
            background: white;
            color: #667eea;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .movers-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }

        .mover-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f0fdf4;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #10b981;
        }

        .mover-ticker {
            font-size: 1.2em;
            font-weight: 700;
            color: #059669;
        }

        .mover-change {
            font-size: 1.1em;
            font-weight: 600;
            color: #065f46;
        }

        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }

        .no-data h2 {
            font-size: 2em;
            margin-bottom: 15px;
            color: #1e293b;
        }

        .refresh-note {
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 25px;
            font-size: 0.95em;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }

            .hot-signals {
                grid-column: span 1;
            }
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Crypto Narrative Tracker</h1>
            <p class="subtitle">Genesis Mode - Catch Emerging Narratives Early</p>
            {% if data %}
            <span class="status-badge">● LIVE</span>
            <p class="last-update">Last updated: {{ last_update }}</p>
            {% endif %}
        </div>

        {% if data %}
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-label">Emerging Tickers</div>
                <div class="stat-value">{{ total_tickers }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💬</div>
                <div class="stat-label">Total Mentions</div>
                <div class="stat-value">{{ total_mentions }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🔥</div>
                <div class="stat-label">Hot Signals</div>
                <div class="stat-value">{{ hot_signals }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-label">Scans Saved</div>
                <div class="stat-value">{{ scans_count }}</div>
            </div>
        </div>

        <div class="main-content">
            <div class="card">
                <h2>📊 Top Emerging Tickers</h2>
                {% for ticker in top_tickers[:15] %}
                <div class="ticker-row">
                    <div class="ticker-rank">#{{ loop.index }}</div>
                    <div class="ticker-symbol">${{ ticker.symbol }}</div>
                    <div class="ticker-mentions">{{ ticker.count }} mentions</div>
                    <div class="ticker-trend">
                        {% if ticker.is_new %}
                        <span class="trend-badge trend-new">🆕 NEW</span>
                        {% elif ticker.change > 0 %}
                        <span class="trend-badge trend-up">🔥 +{{ ticker.change }}</span>
                        {% elif ticker.change < 0 %}
                        <span class="trend-badge trend-down">📉 {{ ticker.change }}</span>
                        {% endif %}
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {{ (ticker.count / max_mentions * 100)|int }}%;"></div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="card hot-signals">
                <h2>🔔 Narrative Alerts</h2>
                {% if hot_keywords %}
                {% for kw in hot_keywords %}
                <div class="signal-item">
                    <div class="signal-keyword">{{ kw.keyword }}</div>
                    <div class="signal-count">{{ kw.count }} mentions detected</div>
                    <div class="signal-tickers">
                        {% for ticker in kw.tickers[:5] %}
                        <span class="signal-ticker">${{ ticker }}</span>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
                {% else %}
                <p style="color: #94a3b8; text-align: center; padding: 20px;">No keyword signals yet. Run the tracker to detect airdrops, launches, and presales!</p>
                {% endif %}
            </div>
        </div>

        {% if movers %}
        <div class="movers-section">
            <h2>🚀 Biggest Movers</h2>
            {% for mover in movers %}
            <div class="mover-item">
                <div class="mover-ticker">${{ mover.ticker }}</div>
                <div class="mover-change">+{{ mover.change }} mentions ({{ mover.previous }} → {{ mover.current }})</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <p class="refresh-note">🔄 Dashboard auto-refreshes every 2 minutes | Run main.py to update data</p>
        {% else %}
        <div class="card">
            <div class="no-data">
                <h2>📭 No Data Yet</h2>
                <p>Run the tracker script to start collecting data!</p>
                <p style="margin-top: 20px; font-family: monospace; background: #f1f5f9; padding: 15px; border-radius: 8px; display: inline-block;">python main.py</p>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''


@app.route('/')
def dashboard():
    result = load_latest_data()

    if not result or result[0] is None:
        return render_template_string(HTML_TEMPLATE, data=None)

    data, scans_count = result

    # Load full history for trends
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            trends = calculate_trends(history)
    except:
        trends = {}

    # Process data
    tickers = data.get('tickers', {})
    timestamp = data.get('timestamp', '')

    # Sort tickers by mentions
    sorted_tickers = sorted(tickers.items(), key=lambda x: x[1], reverse=True)

    # Build ticker list with trends
    top_tickers = []
    max_mentions = max([count for _, count in sorted_tickers
                        ]) if sorted_tickers else 1

    for symbol, count in sorted_tickers[:20]:
        trend_data = trends.get(symbol, {})
        top_tickers.append({
            'symbol': symbol,
            'count': count,
            'change': trend_data.get('change', 0),
            'is_new': trend_data.get('is_new', False),
            'previous': trend_data.get('previous', 0)
        })

    # Calculate movers
    movers = []
    for ticker in top_tickers:
        if ticker['change'] > 0:
            movers.append({
                'ticker': ticker['symbol'],
                'change': ticker['change'],
                'previous': ticker['previous'],
                'current': ticker['count']
            })
    movers = sorted(movers, key=lambda x: x['change'], reverse=True)[:5]

    # Mock hot keywords (you can enhance this by saving keyword data from main.py)
    hot_keywords = [{
        'keyword': 'AIRDROP',
        'count': 5,
        'tickers': ['VOOZ', 'HUNT', 'TAP']
    }, {
        'keyword': 'PRESALE',
        'count': 3,
        'tickers': ['VERDIS', 'TAP']
    }, {
        'keyword': 'LAUNCH',
        'count': 8,
        'tickers': ['KIKI', 'VOOZ', 'HUNT']
    }]

    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp)
        last_update = dt.strftime('%B %d, %Y at %H:%M:%S')
    except:
        last_update = 'Unknown'

    return render_template_string(HTML_TEMPLATE,
                                  data=data,
                                  top_tickers=top_tickers,
                                  total_tickers=len(tickers),
                                  total_mentions=sum(tickers.values()),
                                  hot_signals=len(hot_keywords),
                                  scans_count=scans_count,
                                  max_mentions=max_mentions,
                                  last_update=last_update,
                                  movers=movers,
                                  hot_keywords=hot_keywords)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
