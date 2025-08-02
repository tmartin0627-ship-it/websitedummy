#!/usr/bin/env python3
"""
S&P 500 Stock Prices Web Server
A Flask web server that serves the S&P 500 stock tracking website
and provides API endpoints for real-time stock data.
"""

from flask import Flask, render_template_string, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from sp500_fetcher import SP500DataFetcher
import config

app = Flask(__name__)
CORS(app)  # Enable CORS for API endpoints

# Initialize the stock data fetcher with your Alpha Vantage API key
stock_fetcher = SP500DataFetcher(api_key=config.ALPHA_VANTAGE_API_KEY)

@app.route('/')
def index():
    """Serve the main S&P 500 website"""
    try:
        with open('sp500_stocks.html', 'r') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return """
        <h1>Error: sp500_stocks.html not found</h1>
        <p>Please make sure the sp500_stocks.html file is in the same directory as this server.</p>
        """

@app.route('/api/stocks')
def get_stocks():
    """API endpoint to get all S&P 500 stock data"""
    try:
        stocks_data = stock_fetcher.fetch_all_stocks()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_stocks': len(stocks_data),
            'stocks': stocks_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    """API endpoint to get data for a specific stock"""
    try:
        stock_data = stock_fetcher.get_stock_quote(symbol.upper())
        if stock_data:
            company_info = stock_fetcher.get_company_info(symbol.upper())
            stock_data.update(company_info)
            return jsonify({
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'stock': stock_data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Stock {symbol} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/market-summary')
def get_market_summary():
    """API endpoint to get market summary statistics"""
    try:
        market_summary = stock_fetcher.get_market_summary()
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'market_summary': market_summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/gainers')
def get_gainers():
    """API endpoint to get top gaining stocks"""
    try:
        stocks_data = stock_fetcher.fetch_all_stocks()
        gainers = [s for s in stocks_data if float(s['change_percent']) > 0]
        gainers.sort(key=lambda x: float(x['change_percent']), reverse=True)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_gainers': len(gainers),
            'gainers': gainers[:20]  # Top 20 gainers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/losers')
def get_losers():
    """API endpoint to get top losing stocks"""
    try:
        stocks_data = stock_fetcher.fetch_all_stocks()
        losers = [s for s in stocks_data if float(s['change_percent']) < 0]
        losers.sort(key=lambda x: float(x['change_percent']))
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_losers': len(losers),
            'losers': losers[:20]  # Top 20 losers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/most-active')
def get_most_active():
    """API endpoint to get most actively traded stocks"""
    try:
        stocks_data = stock_fetcher.fetch_all_stocks()
        stocks_data.sort(key=lambda x: x['volume'], reverse=True)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'most_active': stocks_data[:20]  # Top 20 most active
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

def create_sample_data():
    """Create sample data file for testing"""
    print("🔄 Creating sample stock data...")
    stocks_data = stock_fetcher.fetch_all_stocks()
    
    # Save sample data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'sample_sp500_data_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_stocks': len(stocks_data),
            'stocks': stocks_data
        }, f, indent=2)
    
    print(f"💾 Sample data saved to {filename}")
    return filename

if __name__ == '__main__':
    print("🚀 Starting S&P 500 Stock Prices Web Server")
    print("=" * 50)
    
    # Check if HTML file exists
    if not os.path.exists('sp500_stocks.html'):
        print("⚠️  Warning: sp500_stocks.html not found in current directory")
    else:
        print("✅ Found sp500_stocks.html")
    
    # Create sample data
    create_sample_data()
    
    print("\n🌐 Server starting on http://localhost:5000")
    print("\n📚 Available endpoints:")
    print("   🏠 Homepage: http://localhost:5000")
    print("   📊 All stocks: http://localhost:5000/api/stocks")
    print("   📈 Market summary: http://localhost:5000/api/market-summary")
    print("   🟢 Top gainers: http://localhost:5000/api/gainers")
    print("   🔴 Top losers: http://localhost:5000/api/losers")
    print("   📊 Most active: http://localhost:5000/api/most-active")
    print("   💹 Single stock: http://localhost:5000/api/stock/AAPL")
    print("   ❤️  Health check: http://localhost:5000/health")
    
    print("\n💡 Tips:")
    print("   - The website will show demo data by default")
    print("   - Get a free API key from Alpha Vantage for real data")
    print("   - Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=config.DEBUG_MODE, host=config.SERVER_HOST, port=config.SERVER_PORT)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
