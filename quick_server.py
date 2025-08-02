#!/usr/bin/env python3
"""
Quick Start S&P 500 Stock Prices Web Server
A Flask web server that starts immediately and loads data in the background
"""

from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
from sp500_fetcher import SP500DataFetcher
import config

app = Flask(__name__)
CORS(app)

# Global variables for stock data
stocks_data = []
data_loading = True
last_updated = None

# Initialize the stock data fetcher with your Alpha Vantage API key
stock_fetcher = SP500DataFetcher(api_key=config.ALPHA_VANTAGE_API_KEY)

def load_stock_data_background():
    """Load stock data in background thread"""
    global stocks_data, data_loading, last_updated
    
    print("🔄 Loading stock data in background...")
    try:
        stocks_data = stock_fetcher.fetch_all_stocks()
        last_updated = datetime.now()
        print(f"✅ Stock data loaded! {len(stocks_data)} stocks available")
    except Exception as e:
        print(f"❌ Error loading stock data: {e}")
        # Generate demo data as fallback
        stocks_data = stock_fetcher.fetch_all_stocks()
        last_updated = datetime.now()
    finally:
        data_loading = False

@app.route('/')
def index():
    """Serve the main S&P 500 website"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top 5 S&P 500 - Live Stock Tracker</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-bg: #0a0a0a;
            --secondary-bg: #1a1a1a;
            --card-bg: #252525;
            --accent-color: #00d4ff;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --success-color: #00ff88;
            --danger-color: #ff4757;
            --warning-color: #ffa502;
            --border-color: #333;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--primary-bg);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 71, 87, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(0, 255, 136, 0.1) 0%, transparent 50%);
        }

        .header {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(10, 10, 10, 0.9);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--glass-border);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-color), var(--success-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo::before {
            content: "📈";
            font-size: 2rem;
            filter: none;
            -webkit-text-fill-color: initial;
        }

        .market-summary {
            display: flex;
            gap: 32px;
            align-items: center;
        }

        .market-index {
            text-align: center;
            padding: 12px 20px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .market-index:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.08);
        }

        .market-index .name {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 4px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .market-index .value {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .market-index .change {
            font-size: 0.85rem;
            font-weight: 500;
        }

        .positive {
            color: var(--success-color);
        }

        .negative {
            color: var(--danger-color);
        }

        .neutral {
            color: var(--warning-color);
        }

        .main-content {
            padding: 40px 0;
        }

        .loading-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 70vh;
            text-align: center;
        }

        .loading-spinner {
            width: 80px;
            height: 80px;
            border: 3px solid var(--border-color);
            border-top: 3px solid var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 32px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 16px;
            background: linear-gradient(135deg, var(--text-primary), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .loading-details {
            font-size: 1.1rem;
            color: var(--text-secondary);
            max-width: 600px;
            line-height: 1.6;
        }

        .controls {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
            padding: 24px;
            margin-bottom: 32px;
            border-radius: 20px;
        }

        .controls-content {
            display: flex;
            gap: 24px;
            align-items: center;
            flex-wrap: wrap;
        }

        .search-box {
            flex: 1;
            min-width: 300px;
            position: relative;
        }

        .search-input {
            width: 100%;
            padding: 16px 50px 16px 20px;
            border: 2px solid var(--border-color);
            border-radius: 50px;
            background: var(--card-bg);
            color: var(--text-primary);
            font-size: 1rem;
            font-weight: 400;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 4px rgba(0, 212, 255, 0.1);
            background: var(--secondary-bg);
        }

        .search-input::placeholder {
            color: var(--text-secondary);
        }

        .search-icon {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 1.2rem;
        }

        .filter-buttons {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .filter-btn {
            padding: 12px 24px;
            border: 2px solid var(--border-color);
            border-radius: 50px;
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .filter-btn:hover {
            border-color: var(--accent-color);
            color: var(--accent-color);
            transform: translateY(-1px);
        }

        .filter-btn.active {
            background: var(--accent-color);
            border-color: var(--accent-color);
            color: var(--primary-bg);
            box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
        }

        .refresh-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 50px;
            background: linear-gradient(135deg, var(--success-color), #00cc7a);
            color: var(--primary-bg);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 255, 136, 0.4);
        }

        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
            padding: 24px;
            border-radius: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            background: rgba(255, 255, 255, 0.08);
            box-shadow: var(--shadow);
        }

        .stat-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--text-primary), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stocks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 24px;
        }

        .stock-card {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 32px;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }

        .stock-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-color), var(--success-color));
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.4s ease;
        }

        .stock-card:hover {
            transform: translateY(-8px);
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            border-color: var(--accent-color);
        }

        .stock-card:hover::before {
            transform: scaleX(1);
        }

        .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }

        .stock-info {
            flex: 1;
        }

        .stock-symbol {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--accent-color);
            margin-bottom: 4px;
        }

        .stock-name {
            color: var(--text-secondary);
            font-size: 1rem;
            font-weight: 400;
            line-height: 1.4;
        }

        .stock-price {
            font-size: 2.2rem;
            font-weight: 700;
            text-align: right;
        }

        .change-indicator {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 8px;
        }

        .change-arrow {
            font-size: 1.4rem;
            font-weight: bold;
        }

        .change-text {
            font-size: 1rem;
            font-weight: 600;
        }

        .stock-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 24px;
        }

        .financial-metrics {
            grid-column: 1 / -1;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }

        .stock-detail {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stock-detail:hover {
            border-color: var(--accent-color);
            background: rgba(0, 212, 255, 0.05);
        }

        .stock-detail .label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-bottom: 6px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stock-detail .value {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 20px;
            }

            .market-summary {
                gap: 16px;
                overflow-x: auto;
                width: 100%;
                padding-bottom: 8px;
            }

            .market-index {
                min-width: 120px;
            }

            .controls-content {
                flex-direction: column;
                align-items: stretch;
            }

            .search-box {
                min-width: auto;
            }

            .filter-buttons {
                justify-content: center;
                flex-wrap: wrap;
            }

            .stocks-grid {
                grid-template-columns: 1fr;
            }

            .stats-bar {
                grid-template-columns: repeat(2, 1fr);
            }

            .stock-header {
                flex-direction: column;
                gap: 16px;
            }

            .stock-price, .change-indicator {
                text-align: left;
                justify-content: flex-start;
            }
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--primary-bg);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .stock-card {
            animation: fadeInUp 0.6s ease forwards;
        }

        .stock-card:nth-child(1) { animation-delay: 0.1s; }
        .stock-card:nth-child(2) { animation-delay: 0.2s; }
        .stock-card:nth-child(3) { animation-delay: 0.3s; }
        .stock-card:nth-child(4) { animation-delay: 0.4s; }
        .stock-card:nth-child(5) { animation-delay: 0.5s; }

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
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
            padding: 32px;
            width: 90%;
            max-width: 900px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .modal-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .modal-subtitle {
            font-size: 1rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 2rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: color 0.3s ease;
            padding: 8px;
            border-radius: 8px;
        }

        .close-btn:hover {
            color: var(--accent-color);
            background: rgba(255, 255, 255, 0.1);
        }

        .chart-container {
            position: relative;
            height: 400px;
            margin: 24px 0;
            background: var(--card-bg);
            border-radius: 16px;
            padding: 16px;
        }

        .chart-controls {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            justify-content: center;
        }

        .time-btn {
            padding: 8px 16px;
            border: 2px solid var(--border-color);
            border-radius: 20px;
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .time-btn:hover {
            border-color: var(--accent-color);
            color: var(--accent-color);
        }

        .time-btn.active {
            background: var(--accent-color);
            border-color: var(--accent-color);
            color: var(--primary-bg);
        }

        .stock-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 24px;
        }

        .metric-card {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }

        .metric-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--text-primary);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">Top 5 S&P 500</div>
                <div class="market-summary">
                    <div class="market-index">
                        <div class="name">S&P 500</div>
                        <div class="value" id="sp500Value">4,200.50</div>
                        <div class="change positive">+15.25 (+0.36%)</div>
                    </div>
                    <div class="market-index">
                        <div class="name">NASDAQ</div>
                        <div class="value" id="nasdaqValue">13,150.25</div>
                        <div class="change negative">-25.75 (-0.20%)</div>
                    </div>
                    <div class="market-index">
                        <div class="name">DOW</div>
                        <div class="value" id="dowValue">34,850.75</div>
                        <div class="change positive">+125.50 (+0.36%)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container main-content">
        <div id="loadingScreen" class="loading-screen">
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading Top 5 S&P 500 Companies</div>
            <div class="loading-details">
                Fetching live stock prices for Apple, Microsoft, Google, Amazon, and NVIDIA...<br>
                This should only take a few seconds.
            </div>
        </div>

        <div id="mainContent" style="display: none;">
            <div class="controls">
                <div class="controls-content">
                    <div class="search-box">
                        <input type="text" class="search-input" id="searchInput" placeholder="Search by company name or symbol...">
                        <span class="search-icon">🔍</span>
                    </div>
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-filter="all">All</button>
                        <button class="filter-btn" data-filter="gainers">Gainers</button>
                        <button class="filter-btn" data-filter="losers">Losers</button>
                        <button class="filter-btn" data-filter="active">Active</button>
                    </div>
                    <button class="refresh-btn" id="refreshBtn">
                        <span>Refresh</span>
                    </button>
                </div>
            </div>

            <div class="stats-bar">
                <div class="stat-card">
                    <div class="stat-label">Total Stocks</div>
                    <div class="stat-value" id="totalStocks">5</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Gainers</div>
                    <div class="stat-value positive" id="gainersCount">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Losers</div>
                    <div class="stat-value negative" id="losersCount">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Unchanged</div>
                    <div class="stat-value neutral" id="unchangedCount">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Last Updated</div>
                    <div class="stat-value" id="lastUpdated">-</div>
                </div>
            </div>

            <div class="stocks-grid" id="stocksGrid">
                <!-- Stock cards will be populated here -->
            </div>
        </div>
    </div>

    <!-- Modal for historical charts -->
    <div id="stockModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <div class="modal-title" id="modalTitle">Loading...</div>
                    <div class="modal-subtitle" id="modalSubtitle">Historical Price Chart</div>
                </div>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            
            <div class="chart-controls">
                <button class="time-btn active" onclick="changeTimeframe('1M')">1M</button>
                <button class="time-btn" onclick="changeTimeframe('3M')">3M</button>
                <button class="time-btn" onclick="changeTimeframe('6M')">6M</button>
                <button class="time-btn" onclick="changeTimeframe('1Y')">1Y</button>
                <button class="time-btn" onclick="changeTimeframe('2Y')">2Y</button>
            </div>
            
            <div class="chart-container">
                <canvas id="stockChart"></canvas>
            </div>
            
            <div class="stock-metrics" id="stockMetrics">
                <!-- Stock metrics will be populated here -->
            </div>
        </div>
    </div>

    <script>
        class SP500StockTracker {
            constructor() {
                this.stocks = [];
                this.filteredStocks = [];
                this.currentFilter = 'all';
                this.currentPage = 1;
                this.stocksPerPage = 20;
                this.searchTerm = '';
                this.isLoading = true;
                
                this.initializeEventListeners();
                
                // Check data status immediately
                this.checkDataStatus();
                
                // Also check for data every 2 seconds as backup
                this.statusInterval = setInterval(() => {
                    if (this.isLoading) {
                        this.checkDataStatus();
                    }
                }, 2000);
                
                // Emergency fallback: force show content after 10 seconds
                setTimeout(() => {
                    if (this.isLoading) {
                        console.log('Emergency fallback: forcing content display');
                        this.isLoading = false;
                        clearInterval(this.statusInterval);
                        document.getElementById('loadingScreen').style.display = 'none';
                        document.getElementById('mainContent').style.display = 'block';
                        this.loadStockData();
                    }
                }, 10000);
            }

            async checkDataStatus() {
                try {
                    const response = await fetch('/api/data-status');
                    const data = await response.json();
                    
                    console.log('Data status:', data);
                    
                    if (data.data_ready && this.isLoading) {
                        this.isLoading = false;
                        clearInterval(this.statusInterval);
                        document.getElementById('loadingScreen').style.display = 'none';
                        document.getElementById('mainContent').style.display = 'block';
                        this.loadStockData();
                    }
                } catch (error) {
                    console.error('Error checking data status:', error);
                    // Fallback: show main content after 5 seconds if there's an error
                    setTimeout(() => {
                        if (this.isLoading) {
                            console.log('Fallback: showing main content');
                            this.isLoading = false;
                            clearInterval(this.statusInterval);
                            document.getElementById('loadingScreen').style.display = 'none';
                            document.getElementById('mainContent').style.display = 'block';
                            this.loadStockData();
                        }
                    }, 5000);
                }
            }

            initializeEventListeners() {
                // Will be initialized after loading
            }

            async loadStockData() {
                try {
                    const response = await fetch('/api/stocks');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.stocks = data.stocks;
                        this.filterStocks();
                        this.updateStats();
                        this.updateLastUpdated();
                        this.setupEventListeners();
                    }
                } catch (error) {
                    console.error('Error loading stock data:', error);
                }
            }

            setupEventListeners() {
                // Search functionality
                document.getElementById('searchInput').addEventListener('input', (e) => {
                    this.searchTerm = e.target.value.toLowerCase();
                    this.filterStocks();
                });

                // Filter buttons
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                        e.target.classList.add('active');
                        this.currentFilter = e.target.dataset.filter;
                        this.filterStocks();
                    });
                });

                // Refresh button
                document.getElementById('refreshBtn').addEventListener('click', () => {
                    this.loadStockData();
                });
            }

            filterStocks() {
                let filtered = [...this.stocks];

                // Apply search filter
                if (this.searchTerm) {
                    filtered = filtered.filter(stock => 
                        stock.symbol.toLowerCase().includes(this.searchTerm) ||
                        stock.name.toLowerCase().includes(this.searchTerm) ||
                        (stock.sector && stock.sector.toLowerCase().includes(this.searchTerm))
                    );
                }

                // Apply category filter
                switch (this.currentFilter) {
                    case 'gainers':
                        filtered = filtered.filter(stock => parseFloat(stock.change_percent) > 0)
                                         .sort((a, b) => parseFloat(b.change_percent) - parseFloat(a.change_percent));
                        break;
                    case 'losers':
                        filtered = filtered.filter(stock => parseFloat(stock.change_percent) < 0)
                                         .sort((a, b) => parseFloat(a.change_percent) - parseFloat(b.change_percent));
                        break;
                    case 'active':
                        filtered = filtered.sort((a, b) => b.volume - a.volume);
                        break;
                    default:
                        filtered = filtered.sort((a, b) => a.symbol.localeCompare(b.symbol));
                }

                this.filteredStocks = filtered;
                this.renderStocks();
            }

            renderStocks() {
                const stocksGrid = document.getElementById('stocksGrid');
                
                if (this.filteredStocks.length === 0) {
                    stocksGrid.innerHTML = '<div style="text-align: center; color: #95a5a6; grid-column: 1 / -1;">No stocks found matching your criteria.</div>';
                    return;
                }

                const stockCardsHtml = this.filteredStocks.slice(0, this.stocksPerPage).map(stock => {
                    return this.createStockCard(stock);
                }).join('');
                
                stocksGrid.innerHTML = stockCardsHtml;
                
                // Add click event listeners to all stock cards
                const stockCards = stocksGrid.querySelectorAll('.stock-card');
                stockCards.forEach((card, index) => {
                    const stock = this.filteredStocks[index];
                    card.addEventListener('click', () => this.showStockChart(stock));
                    card.style.cursor = 'pointer';
                });
            }

            createStockCard(stock) {
                const changePercent = parseFloat(stock.change_percent);
                const change = parseFloat(stock.change);
                const changeClass = changePercent > 0 ? 'positive' : changePercent < 0 ? 'negative' : 'neutral';
                const changeArrow = changePercent > 0 ? '📈' : changePercent < 0 ? '📉' : '➡️';

                return `
                    <div class="stock-card">
                        <div class="stock-header">
                            <div class="stock-info">
                                <div class="stock-symbol">${stock.symbol}</div>
                                <div class="stock-name">${stock.name || stock.symbol + ' Corporation'}</div>
                            </div>
                            <div>
                                <div class="stock-price ${changeClass}">$${parseFloat(stock.price).toFixed(2)}</div>
                                <div class="change-indicator">
                                    <span class="change-arrow">${changeArrow}</span>
                                    <span class="change-text ${changeClass}">
                                        ${change >= 0 ? '+' : ''}${change.toFixed(2)} 
                                        (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="stock-details">
                            <div class="stock-detail">
                                <div class="label">Volume</div>
                                <div class="value">${this.formatNumber(stock.volume)}</div>
                            </div>
                            <div class="stock-detail">
                                <div class="label">Sector</div>
                                <div class="value">${stock.sector || 'Technology'}</div>
                            </div>
                            <div class="stock-detail">
                                <div class="label">High</div>
                                <div class="value">$${parseFloat(stock.high || stock.price).toFixed(2)}</div>
                            </div>
                            <div class="stock-detail">
                                <div class="label">Low</div>
                                <div class="value">$${parseFloat(stock.low || stock.price).toFixed(2)}</div>
                            </div>
                            
                            <div class="financial-metrics">
                                <div class="stock-detail">
                                    <div class="label">Market Cap</div>
                                    <div class="value">${this.formatFinancial(stock.market_cap)}</div>
                                </div>
                                <div class="stock-detail">
                                    <div class="label">Enterprise Value</div>
                                    <div class="value">${this.formatFinancial(stock.enterprise_value)}</div>
                                </div>
                                <div class="stock-detail">
                                    <div class="label">LTM Revenue</div>
                                    <div class="value">${this.formatFinancial(stock.ltm_revenue)}</div>
                                </div>
                                <div class="stock-detail">
                                    <div class="label">LTM EBITDA</div>
                                    <div class="value">${this.formatFinancial(stock.ltm_ebitda)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                const cardElement = document.createElement('div');
                cardElement.className = 'stock-card';
                cardElement.innerHTML = cardHtml;
                cardElement.addEventListener('click', () => this.showStockChart(stock));
                
                return cardHtml;

            updateStats() {
                const gainers = this.stocks.filter(stock => parseFloat(stock.change_percent) > 0).length;
                const losers = this.stocks.filter(stock => parseFloat(stock.change_percent) < 0).length;
                const unchanged = this.stocks.filter(stock => parseFloat(stock.change_percent) === 0).length;

                document.getElementById('gainersCount').textContent = gainers;
                document.getElementById('losersCount').textContent = losers;
                document.getElementById('unchangedCount').textContent = unchanged;
                document.getElementById('totalStocks').textContent = this.stocks.length;
            }

            updateLastUpdated() {
                const now = new Date();
                const timeString = now.toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit'
                });
                document.getElementById('lastUpdated').textContent = timeString;
            }

            formatNumber(num) {
                if (num >= 1000000000) {
                    return (num / 1000000000).toFixed(1) + 'B';
                } else if (num >= 1000000) {
                    return (num / 1000000).toFixed(1) + 'M';
                } else if (num >= 1000) {
                    return (num / 1000).toFixed(1) + 'K';
                }
                return num.toString();
            }

            formatFinancial(num) {
                if (!num || num === 0) return 'N/A';
                
                if (num >= 1000000000000) {
                    return '$' + (num / 1000000000000).toFixed(2) + 'T';
                } else if (num >= 1000000000) {
                    return '$' + (num / 1000000000).toFixed(2) + 'B';
                } else if (num >= 1000000) {
                    return '$' + (num / 1000000).toFixed(2) + 'M';
                } else if (num >= 1000) {
                    return '$' + (num / 1000).toFixed(2) + 'K';
                }
                return '$' + num.toFixed(2);
            }

            // Modal functionality
            showStockChart(stock) {
                const modal = document.getElementById('stockModal');
                const modalTitle = document.getElementById('modalTitle');
                const modalSubtitle = document.getElementById('modalSubtitle');
                const stockMetrics = document.getElementById('stockMetrics');
                
                modalTitle.textContent = `${stock.name || stock.symbol + ' Corporation'}`;
                modalSubtitle.textContent = `${stock.symbol} - Historical Price Chart`;
                
                // Populate stock metrics
                stockMetrics.innerHTML = `
                    <div class="metric-card">
                        <div class="metric-label">Current Price</div>
                        <div class="metric-value">$${parseFloat(stock.price).toFixed(2)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Market Cap</div>
                        <div class="metric-value">${this.formatFinancial(stock.market_cap)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Enterprise Value</div>
                        <div class="metric-value">${this.formatFinancial(stock.enterprise_value)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">LTM Revenue</div>
                        <div class="metric-value">${this.formatFinancial(stock.ltm_revenue)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">LTM EBITDA</div>
                        <div class="metric-value">${this.formatFinancial(stock.ltm_ebitda)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Day Change</div>
                        <div class="metric-value ${parseFloat(stock.change_percent) >= 0 ? 'positive' : 'negative'}">
                            ${parseFloat(stock.change_percent) >= 0 ? '+' : ''}${parseFloat(stock.change_percent).toFixed(2)}%
                        </div>
                    </div>
                `;
                
                modal.style.display = 'block';
                this.currentStock = stock;
                this.generateHistoricalChart(stock, '1M');
            }
            
            generateHistoricalChart(stock, timeframe) {
                const ctx = document.getElementById('stockChart').getContext('2d');
                
                // Destroy existing chart if it exists
                if (this.chartInstance) {
                    this.chartInstance.destroy();
                }
                
                // Generate sample historical data based on current price
                const currentPrice = parseFloat(stock.price);
                const dataPoints = this.generateSampleChartData(currentPrice, timeframe);
                
                this.chartInstance = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: dataPoints.labels,
                        datasets: [{
                            label: `${stock.symbol} Price`,
                            data: dataPoints.prices,
                            borderColor: '#00d4ff',
                            backgroundColor: 'rgba(0, 212, 255, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 0,
                            pointHoverRadius: 6,
                            pointHoverBackgroundColor: '#00d4ff',
                            pointHoverBorderColor: '#ffffff',
                            pointHoverBorderWidth: 2
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
                                backgroundColor: 'rgba(20, 20, 30, 0.9)',
                                titleColor: '#ffffff',
                                bodyColor: '#ffffff',
                                borderColor: '#00d4ff',
                                borderWidth: 1,
                                cornerRadius: 8,
                                displayColors: false
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
                                    maxTicksLimit: 8
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
                                    callback: function(value) {
                                        return '$' + value.toFixed(2);
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
            
            generateSampleChartData(currentPrice, timeframe) {
                const dataPoints = {
                    '1M': { count: 30, label: 'day' },
                    '3M': { count: 90, label: 'day' },
                    '6M': { count: 180, label: 'day' },
                    '1Y': { count: 365, label: 'day' },
                    '2Y': { count: 730, label: 'day' }
                };
                
                const config = dataPoints[timeframe];
                const labels = [];
                const prices = [];
                
                // Generate realistic price movement
                let price = currentPrice * 0.8; // Start at 80% of current price
                const volatility = currentPrice * 0.02; // 2% daily volatility
                const trend = (currentPrice - price) / config.count; // Overall upward trend
                
                for (let i = 0; i < config.count; i++) {
                    const date = new Date();
                    date.setDate(date.getDate() - (config.count - i));
                    
                    if (timeframe === '1M' || timeframe === '3M') {
                        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
                    } else {
                        labels.push(date.toLocaleDateString('en-US', { year: '2-digit', month: 'short' }));
                    }
                    
                    // Add some randomness with overall trend
                    const randomChange = (Math.random() - 0.5) * volatility;
                    price += trend + randomChange;
                    prices.push(parseFloat(price.toFixed(2)));
                }
                
                return { labels, prices };
            }
        }

        // Initialize the stock tracker
        let stockTracker;
        
        // Global modal functions
        function closeModal() {
            const modal = document.getElementById('stockModal');
            modal.style.display = 'none';
            
            // Destroy chart when closing modal
            if (stockTracker && stockTracker.chartInstance) {
                stockTracker.chartInstance.destroy();
                stockTracker.chartInstance = null;
            }
        }
        
        function changeTimeframe(timeframe) {
            // Update active button
            document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Regenerate chart with new timeframe
            if (stockTracker && stockTracker.currentStock) {
                stockTracker.generateHistoricalChart(stockTracker.currentStock, timeframe);
            }
        }
        
        // Close modal when clicking outside of it
        window.addEventListener('click', (event) => {
            const modal = document.getElementById('stockModal');
            if (event.target === modal) {
                closeModal();
            }
        });
        
        // Close modal on escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeModal();
            }
        });
        
        document.addEventListener('DOMContentLoaded', () => {
            stockTracker = new SP500StockTracker();
        });
    </script>
</body>
</html>
    """
    return html_content

@app.route('/api/data-status')
def get_data_status():
    """Check if stock data is ready"""
    return jsonify({
        'data_ready': not data_loading,
        'stocks_count': len(stocks_data),
        'last_updated': last_updated.isoformat() if last_updated else None
    })

@app.route('/api/stocks')
def get_stocks():
    """API endpoint to get all S&P 500 stock data"""
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'total_stocks': len(stocks_data),
        'stocks': stocks_data
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loading': data_loading,
        'stocks_count': len(stocks_data),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Quick Start S&P 500 Stock Prices Web Server")
    print("=" * 50)
    
    # Start background data loading
    data_thread = threading.Thread(target=load_stock_data_background, daemon=True)
    data_thread.start()
    
    print("🌐 Server starting immediately on http://localhost:5000")
    print("📊 Stock data loading in background...")
    print("💡 The website will show a loading screen until data is ready")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
