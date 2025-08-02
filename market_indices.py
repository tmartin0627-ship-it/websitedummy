#!/usr/bin/env python3
"""
Market Indices Tracker - S&P 500, NASDAQ, Dow Jones
Simple, clean interface showing major market movements with historical charts
"""

from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Global data storage
indices_data = []
data_loading = True
last_updated = None

def generate_index_data():
    """Generate realistic market index data"""
    return [
        {
            'name': 'S&P 500',
            'symbol': 'SPX',
            'value': 4847.69,
            'change': 23.45,
            'change_percent': 0.49,
            'description': 'Standard & Poor\'s 500'
        },
        {
            'name': 'NASDAQ',
            'symbol': 'IXIC',
            'value': 15234.78,
            'change': -67.23,
            'change_percent': -0.44,
            'description': 'NASDAQ Composite Index'
        },
        {
            'name': 'Dow Jones',
            'symbol': 'DJI',
            'value': 38789.12,
            'change': 145.67,
            'change_percent': 0.38,
            'description': 'Dow Jones Industrial Average'
        }
    ]

def generate_historical_data(current_value, symbol, timeframe='1Y'):
    """Generate realistic historical data for different timeframes"""
    data_points = []
    labels = []
    
    # Define timeframe configurations
    timeframe_config = {
        '1D': {'days': 1, 'interval_hours': 1, 'points': 24},
        '1M': {'days': 30, 'interval_hours': 24, 'points': 30},
        '3M': {'days': 90, 'interval_hours': 24, 'points': 90},
        '1Y': {'days': 365, 'interval_hours': 24, 'points': 365},
        '5Y': {'days': 1825, 'interval_hours': 168, 'points': 260},  # Weekly data points
        '10Y': {'days': 3650, 'interval_hours': 336, 'points': 260}  # Bi-weekly data points
    }
    
    config = timeframe_config.get(timeframe, timeframe_config['1Y'])
    start_date = datetime.now() - timedelta(days=config['days'])
    
    # Generate starting value (varies based on timeframe)
    if timeframe == '1D':
        base_value = current_value * (0.98 + random.random() * 0.04)  # 2% daily range
    elif timeframe in ['1M', '3M']:
        base_value = current_value * (0.85 + random.random() * 0.30)  # 15% range
    elif timeframe == '1Y':
        base_value = current_value * (0.70 + random.random() * 0.60)  # 30% range
    else:  # 5Y, 10Y
        base_value = current_value * (0.30 + random.random() * 0.40)  # Large historical range
    
    # Different volatility for different indices and timeframes
    volatility_map = {
        '1D': {'SPX': 0.005, 'IXIC': 0.008, 'DJI': 0.004},
        '1M': {'SPX': 0.015, 'IXIC': 0.025, 'DJI': 0.012},
        '3M': {'SPX': 0.015, 'IXIC': 0.025, 'DJI': 0.012},
        '1Y': {'SPX': 0.015, 'IXIC': 0.025, 'DJI': 0.012},
        '5Y': {'SPX': 0.020, 'IXIC': 0.030, 'DJI': 0.015},
        '10Y': {'SPX': 0.025, 'IXIC': 0.035, 'DJI': 0.018}
    }
    
    volatility = volatility_map[timeframe].get(symbol, 0.015)
    trend = (current_value - base_value) / config['points']  # Overall trend
    
    # Generate data points
    for i in range(config['points']):
        if timeframe == '1D':
            # Hourly data for 1 day
            point_date = start_date + timedelta(hours=i)
            date_format = point_date.strftime('%H:%M')
        elif timeframe in ['1M', '3M']:
            # Daily data
            point_date = start_date + timedelta(days=i)
            date_format = point_date.strftime('%m/%d')
        elif timeframe == '1Y':
            # Daily data but show monthly labels
            point_date = start_date + timedelta(days=i)
            if i % 30 == 0:  # Show every 30th day
                date_format = point_date.strftime('%b %Y')
            else:
                date_format = ''
        else:  # 5Y, 10Y
            # Longer intervals
            interval_days = config['days'] // config['points']
            point_date = start_date + timedelta(days=i * interval_days)
            date_format = point_date.strftime('%Y')
        
        # Skip weekends for more realistic data (except for 1D view)
        if timeframe != '1D' and point_date.weekday() >= 5:
            continue
            
        # Add trend + random movement
        daily_change = trend + (random.random() - 0.5) * base_value * volatility
        base_value += daily_change
        
        # Ensure we don't go negative
        base_value = max(base_value, current_value * 0.1)
        
        if date_format:  # Only add non-empty labels
            labels.append(date_format)
            data_points.append(round(base_value, 2))
    
    return labels, data_points

def load_indices_data():
    """Load market indices data"""
    global indices_data, data_loading, last_updated
    
    try:
        print("🔄 Loading market indices data...")
        indices_data = generate_index_data()
        last_updated = datetime.now()
        print(f"✅ Successfully loaded {len(indices_data)} market indices")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
    finally:
        data_loading = False

@app.route('/')
def index():
    """Serve the market indices website"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Indices Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-bg: #0a0e1a;
            --secondary-bg: #1a1f35;
            --card-bg: rgba(26, 31, 53, 0.8);
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #95a5a6;
            --accent-color: #00d4ff;
            --positive-color: #27ae60;
            --negative-color: #e74c3c;
            --border-color: rgba(255, 255, 255, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 60px;
        }

        .title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #00d4ff 0%, #ffffff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
        }

        .subtitle {
            font-size: 1.2rem;
            color: var(--text-secondary);
            font-weight: 400;
        }

        .indices-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 32px;
            margin-bottom: 40px;
        }

        .index-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 40px 32px;
            cursor: pointer;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }

        .index-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-color), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .index-card:hover {
            transform: translateY(-8px);
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--accent-color);
            box-shadow: 0 20px 60px rgba(0, 212, 255, 0.2);
        }

        .index-card:hover::before {
            opacity: 1;
        }

        .index-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 24px;
        }

        .index-info h3 {
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
        }

        .index-description {
            font-size: 0.95rem;
            color: var(--text-secondary);
        }

        .index-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 16px;
        }

        .change-container {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .change-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 1rem;
        }

        .positive {
            color: var(--positive-color);
            background: rgba(39, 174, 96, 0.1);
            border: 1px solid rgba(39, 174, 96, 0.3);
        }

        .negative {
            color: var(--negative-color);
            background: rgba(231, 76, 60, 0.1);
            border: 1px solid rgba(231, 76, 60, 0.3);
        }

        .change-arrow {
            font-size: 1.2rem;
        }

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(15px);
            animation: fadeIn 0.3s ease;
        }

        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--secondary-bg);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 40px;
            width: 95%;
            max-width: 1000px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .modal-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .modal-subtitle {
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-top: 8px;
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 2.5rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            padding: 12px;
            border-radius: 12px;
        }

        .close-btn:hover {
            color: var(--accent-color);
            background: rgba(255, 255, 255, 0.1);
            transform: scale(1.1);
        }

        .chart-controls {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .time-btn {
            padding: 10px 20px;
            border: 2px solid var(--border-color);
            border-radius: 25px;
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .time-btn:hover {
            border-color: var(--accent-color);
            color: var(--accent-color);
            transform: translateY(-2px);
        }

        .time-btn.active {
            background: var(--accent-color);
            border-color: var(--accent-color);
            color: var(--primary-bg);
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        }

        .chart-container {
            position: relative;
            height: 500px;
            margin: 32px 0;
            background: var(--card-bg);
            border-radius: 20px;
            padding: 24px;
            border: 1px solid var(--border-color);
        }

        .last-updated {
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @media (max-width: 768px) {
            .title {
                font-size: 2.5rem;
            }
            
            .indices-grid {
                grid-template-columns: 1fr;
                gap: 24px;
            }
            
            .index-card {
                padding: 32px 24px;
            }
            
            .index-value {
                font-size: 2rem;
            }
            
            .modal-content {
                width: 98%;
                padding: 24px;
            }
            
            .chart-container {
                height: 400px;
                padding: 16px;
            }
            
            .chart-controls {
                gap: 8px;
            }
            
            .time-btn {
                padding: 8px 12px;
                font-size: 0.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Market Indices</h1>
            <p class="subtitle">Track major market movements in real-time</p>
        </div>
        
        <div class="indices-grid" id="indicesGrid">
            <!-- Index cards will be populated here -->
        </div>
        
        <div class="last-updated" id="lastUpdated">
            Last updated: Loading...
        </div>
    </div>

    <!-- Modal for historical charts -->
    <div id="chartModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <div class="modal-title" id="modalTitle">Loading...</div>
                    <div class="modal-subtitle">Historical Price Chart</div>
                </div>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            
            <div class="chart-controls">
                <button class="time-btn" onclick="changeTimeframe('1D')">1 Day</button>
                <button class="time-btn" onclick="changeTimeframe('1M')">1 Month</button>
                <button class="time-btn" onclick="changeTimeframe('3M')">3 Months</button>
                <button class="time-btn active" onclick="changeTimeframe('1Y')">1 Year</button>
                <button class="time-btn" onclick="changeTimeframe('5Y')">5 Years</button>
                <button class="time-btn" onclick="changeTimeframe('10Y')">10 Years</button>
            </div>
            
            <div class="chart-container">
                <canvas id="indexChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        class MarketIndicesTracker {
            constructor() {
                this.indices = [];
                this.chartInstance = null;
                this.loadData();
            }

            async loadData() {
                try {
                    const response = await fetch('/api/indices');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.indices = data.indices;
                        this.renderIndices();
                        this.updateLastUpdated(data.timestamp);
                    }
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }

            renderIndices() {
                const grid = document.getElementById('indicesGrid');
                grid.innerHTML = this.indices.map(index => this.createIndexCard(index)).join('');
                
                // Add click event listeners
                const cards = grid.querySelectorAll('.index-card');
                cards.forEach((card, i) => {
                    card.addEventListener('click', () => this.showChart(this.indices[i]));
                });
            }

            createIndexCard(index) {
                const changePercent = parseFloat(index.change_percent);
                const change = parseFloat(index.change);
                const changeClass = changePercent >= 0 ? 'positive' : 'negative';
                const changeArrow = changePercent >= 0 ? '▲' : '▼';

                return `
                    <div class="index-card">
                        <div class="index-header">
                            <div class="index-info">
                                <h3>${index.name}</h3>
                                <div class="index-description">${index.description}</div>
                            </div>
                        </div>
                        <div class="index-value">${index.value.toLocaleString()}</div>
                        <div class="change-container">
                            <div class="change-indicator ${changeClass}">
                                <span class="change-arrow">${changeArrow}</span>
                                <span>${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)</span>
                            </div>
                        </div>
                    </div>
                `;
            }

            async showChart(index) {
                const modal = document.getElementById('chartModal');
                const modalTitle = document.getElementById('modalTitle');
                
                modalTitle.textContent = `${index.name} (${index.symbol})`;
                modal.style.display = 'block';
                
                // Store current index for timeframe changes
                this.currentIndex = index;
                
                // Load default timeframe (1Y)
                await this.loadChartData('1Y');
            }

            async loadChartData(timeframe) {
                if (!this.currentIndex) return;
                
                try {
                    const response = await fetch(`/api/historical/${this.currentIndex.symbol}?timeframe=${timeframe}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        this.generateChart(this.currentIndex, data.historical_data, timeframe);
                        
                        // Update modal subtitle
                        const subtitle = document.querySelector('.modal-subtitle');
                        const timeframeNames = {
                            '1D': '1 Day',
                            '1M': '1 Month', 
                            '3M': '3 Months',
                            '1Y': '1 Year',
                            '5Y': '5 Years',
                            '10Y': '10 Years'
                        };
                        subtitle.textContent = `${timeframeNames[timeframe]} Historical Chart`;
                    }
                } catch (error) {
                    console.error('Error loading historical data:', error);
                }
            }

            generateChart(index, historicalData, timeframe) {
                const ctx = document.getElementById('indexChart').getContext('2d');
                
                // Destroy existing chart
                if (this.chartInstance) {
                    this.chartInstance.destroy();
                }

                const changePercent = parseFloat(index.change_percent);
                const lineColor = changePercent >= 0 ? '#27ae60' : '#e74c3c';
                
                // Adjust point display based on timeframe
                const pointRadius = timeframe === '1D' ? 2 : 0;
                const pointHoverRadius = timeframe === '1D' ? 6 : 8;
                
                this.chartInstance = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: historicalData.labels,
                        datasets: [{
                            label: index.name,
                            data: historicalData.values,
                            borderColor: lineColor,
                            backgroundColor: lineColor + '20',
                            borderWidth: timeframe === '1D' ? 2 : 3,
                            fill: true,
                            tension: timeframe === '1D' ? 0.1 : 0.4,
                            pointRadius: pointRadius,
                            pointHoverRadius: pointHoverRadius,
                            pointHoverBackgroundColor: lineColor,
                            pointHoverBorderColor: '#ffffff',
                            pointHoverBorderWidth: 3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false,
                                backgroundColor: 'rgba(10, 14, 26, 0.95)',
                                titleColor: '#ffffff',
                                bodyColor: '#ffffff',
                                borderColor: lineColor,
                                borderWidth: 2,
                                cornerRadius: 12,
                                displayColors: false,
                                titleFont: { size: 14, weight: 'bold' },
                                bodyFont: { size: 13 },
                                padding: 12,
                                callbacks: {
                                    title: function(context) {
                                        if (timeframe === '1D') {
                                            return `Time: ${context[0].label}`;
                                        }
                                        return context[0].label;
                                    },
                                    label: function(context) {
                                        return `${index.name}: ${context.parsed.y.toLocaleString()}`;
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                display: true,
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)',
                                    drawBorder: false
                                },
                                ticks: {
                                    color: '#95a5a6',
                                    maxTicksLimit: timeframe === '1D' ? 12 : 8,
                                    font: { size: 11 }
                                }
                            },
                            y: {
                                display: true,
                                position: 'right',
                                grid: {
                                    color: 'rgba(255, 255, 255, 0.1)',
                                    drawBorder: false
                                },
                                ticks: {
                                    color: '#95a5a6',
                                    font: { size: 11 },
                                    callback: function(value) {
                                        return value.toLocaleString();
                                    }
                                }
                            }
                        },
                        interaction: {
                            mode: 'index',
                            intersect: false
                        },
                        elements: {
                            line: {
                                borderJoinStyle: 'round'
                            }
                        }
                    }
                });
            }

            updateLastUpdated(timestamp) {
                const date = new Date(timestamp);
                const timeString = date.toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                document.getElementById('lastUpdated').textContent = `Last updated: ${timeString}`;
            }
        }

        // Global functions
        function closeModal() {
            const modal = document.getElementById('chartModal');
            modal.style.display = 'none';
            
            if (window.tracker && window.tracker.chartInstance) {
                window.tracker.chartInstance.destroy();
                window.tracker.chartInstance = null;
            }
        }

        function changeTimeframe(timeframe) {
            // Update active button
            document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Load new chart data
            if (window.tracker) {
                window.tracker.loadChartData(timeframe);
            }
        }

        // Close modal on escape key or outside click
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });

        window.addEventListener('click', (e) => {
            const modal = document.getElementById('chartModal');
            if (e.target === modal) closeModal();
        });

        // Initialize tracker
        document.addEventListener('DOMContentLoaded', () => {
            window.tracker = new MarketIndicesTracker();
        });
    </script>
</body>
</html>
    """
    return html_content

@app.route('/api/indices')
def get_indices():
    """API endpoint to get market indices data"""
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'indices': indices_data
    })

@app.route('/api/historical/<symbol>')
def get_historical_data(symbol):
    """Get historical data for a specific index"""
    from flask import request
    
    # Get timeframe from query parameter, default to 1Y
    timeframe = request.args.get('timeframe', '1Y')
    
    # Find the index
    index = next((idx for idx in indices_data if idx['symbol'] == symbol), None)
    
    if not index:
        return jsonify({'success': False, 'error': 'Index not found'})
    
    # Generate historical data for the specified timeframe
    labels, values = generate_historical_data(index['value'], symbol, timeframe)
    
    return jsonify({
        'success': True,
        'symbol': symbol,
        'timeframe': timeframe,
        'historical_data': {
            'labels': labels,
            'values': values
        }
    })

if __name__ == '__main__':
    import os
    
    print("🚀 Market Indices Tracker")
    print("=" * 40)
    
    # Load data immediately
    load_indices_data()
    
    print("🌐 Server starting...")
    print("📊 Market indices data loaded")
    print("💡 Click on any index to view historical chart")
    
    # Get port from environment variable (for deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    app.run(debug=False, host=host, port=port)
