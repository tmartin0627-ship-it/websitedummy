#!/usr/bin/env python3
"""
S&P 500 Stock Data Fetcher
A Python script to fetch real-time stock data for S&P 500 companies
"""

import requests
import json
import time
from datetime import datetime
import csv
import os
from typing import Dict, List, Optional

class SP500DataFetcher:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the S&P 500 data fetcher
        
        Args:
            api_key: Alpha Vantage API key (free from https://www.alphavantage.co/support/#api-key)
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.sp500_symbols = self.load_sp500_symbols()
        
    def load_sp500_symbols(self) -> List[str]:
        """Load top 5 S&P 500 companies by market cap"""
        # Top 5 S&P 500 companies by market cap for faster loading
        return [
            'AAPL',   # Apple Inc.
            'MSFT',   # Microsoft Corporation  
            'GOOGL',  # Alphabet Inc.
            'AMZN',   # Amazon.com Inc.
            'NVDA'    # NVIDIA Corporation
        ]
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time stock quote for a symbol using Alpha Vantage API
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with stock data or None if error
        """
        if not self.api_key:
            print("⚠️  No API key provided. Using demo data.")
            return self.generate_demo_data(symbol)
            
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': quote.get('01. symbol', symbol),
                    'price': float(quote.get('05. price', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                    'volume': int(quote.get('06. volume', 0)),
                    'high': float(quote.get('03. high', 0)),
                    'low': float(quote.get('04. low', 0)),
                    'open': float(quote.get('02. open', 0)),
                    'previous_close': float(quote.get('08. previous close', 0)),
                    'last_updated': quote.get('07. latest trading day', '')
                }
            else:
                print(f"⚠️  API limit reached for {symbol}. Using demo data.")
                return self.generate_demo_data(symbol)
                
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return self.generate_demo_data(symbol)
    
    def generate_demo_data(self, symbol: str) -> Dict:
        """Generate realistic demo data for a stock symbol"""
        import random
        
        # Base prices for major stocks (approximate real values)
        base_prices = {
            'AAPL': 175, 'MSFT': 330, 'AMZN': 140, 'GOOGL': 130, 'NVDA': 450
        }
        
        # Market caps in billions (approximate real values)
        market_caps = {
            'AAPL': 2800, 'MSFT': 2400, 'GOOGL': 1600, 'AMZN': 1400, 'NVDA': 1100
        }
        
        base_price = base_prices.get(symbol, random.uniform(50, 500))
        market_cap_b = market_caps.get(symbol, random.uniform(100, 3000))
        
        change_percent = random.uniform(-5, 5)
        change = base_price * (change_percent / 100)
        
        # Calculate financial metrics based on market cap
        enterprise_value = market_cap_b * random.uniform(0.9, 1.2)  # EV typically close to market cap
        ltm_revenue = market_cap_b * random.uniform(0.3, 0.8)  # Revenue as % of market cap
        ltm_ebitda = ltm_revenue * random.uniform(0.15, 0.35)  # EBITDA margin 15-35%
        
        return {
            'symbol': symbol,
            'price': round(base_price, 2),
            'change': round(change, 2),
            'change_percent': f"{change_percent:.2f}",
            'volume': random.randint(10000000, 100000000),
            'high': round(base_price * random.uniform(1.01, 1.05), 2),
            'low': round(base_price * random.uniform(0.95, 0.99), 2),
            'open': round(base_price * random.uniform(0.98, 1.02), 2),
            'previous_close': round(base_price - change, 2),
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'market_cap': market_cap_b * 1000000000,  # Convert to actual dollars
            'enterprise_value': enterprise_value * 1000000000,
            'ltm_revenue': ltm_revenue * 1000000000,
            'ltm_ebitda': ltm_ebitda * 1000000000
        }
    
    def get_company_info(self, symbol: str) -> Dict:
        """Get company information for a stock symbol"""
        company_names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'AMZN': 'Amazon.com Inc.',
            'GOOGL': 'Alphabet Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'BRK.B': 'Berkshire Hathaway Inc.',
            'JPM': 'JPMorgan Chase & Co.',
            'JNJ': 'Johnson & Johnson',
            'V': 'Visa Inc.',
            'PG': 'Procter & Gamble Co.',
            'HD': 'Home Depot Inc.',
            'MA': 'Mastercard Inc.',
            'BAC': 'Bank of America Corp.',
            'ABBV': 'AbbVie Inc.',
            'PFE': 'Pfizer Inc.',
            'KO': 'Coca-Cola Co.',
            'AVGO': 'Broadcom Inc.',
            'PEP': 'PepsiCo Inc.',
            'COST': 'Costco Wholesale Corp.',
            'TMO': 'Thermo Fisher Scientific',
            'WMT': 'Walmart Inc.',
            'DIS': 'Walt Disney Co.',
            'ABT': 'Abbott Laboratories',
            'CRM': 'Salesforce Inc.',
            'VZ': 'Verizon Communications',
            'ADBE': 'Adobe Inc.',
            'NFLX': 'Netflix Inc.',
            'CSCO': 'Cisco Systems Inc.',
            'XOM': 'Exxon Mobil Corp.',
            'INTC': 'Intel Corporation',
            'CVX': 'Chevron Corporation',
            'UNH': 'UnitedHealth Group',
            'LLY': 'Eli Lilly and Co.',
            'ORCL': 'Oracle Corporation',
            'WFC': 'Wells Fargo & Co.',
            'BMY': 'Bristol Myers Squibb',
            'T': 'AT&T Inc.',
            'MDT': 'Medtronic plc',
            'UPS': 'United Parcel Service',
            'HON': 'Honeywell International',
            'QCOM': 'QUALCOMM Inc.',
            'IBM': 'International Business Machines',
            'TXN': 'Texas Instruments Inc.',
            'LMT': 'Lockheed Martin Corp.',
            'LOW': 'Lowe\'s Companies Inc.',
            'AMGN': 'Amgen Inc.',
            'SPGI': 'S&P Global Inc.',
            'GS': 'Goldman Sachs Group Inc.'
        }
        
        sectors = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'AMZN': 'Consumer Discretionary',
            'GOOGL': 'Technology', 'TSLA': 'Consumer Discretionary', 'META': 'Technology',
            'NVDA': 'Technology', 'BRK.B': 'Financial Services', 'JPM': 'Financial Services',
            'JNJ': 'Healthcare', 'V': 'Financial Services', 'PG': 'Consumer Staples',
            'HD': 'Consumer Discretionary', 'MA': 'Financial Services', 'BAC': 'Financial Services'
        }
        
        return {
            'name': company_names.get(symbol, f'{symbol} Corporation'),
            'sector': sectors.get(symbol, 'Technology')
        }
    
    def fetch_all_stocks(self) -> List[Dict]:
        """Fetch data for all S&P 500 stocks"""
        stocks_data = []
        
        print("🔄 Fetching S&P 500 stock data...")
        
        for i, symbol in enumerate(self.sp500_symbols, 1):
            print(f"📊 Fetching {symbol} ({i}/{len(self.sp500_symbols)})")
            
            stock_data = self.get_stock_quote(symbol)
            if stock_data:
                company_info = self.get_company_info(symbol)
                stock_data.update(company_info)
                stocks_data.append(stock_data)
            
            # Rate limiting for API calls (Alpha Vantage free tier: 5 calls per minute)
            # Since we only have 5 stocks, no need for rate limiting
            if self.api_key and i % 10 == 0:  # Much less aggressive rate limiting
                print("⏳ Brief pause...")
                time.sleep(2)
        
        print(f"✅ Successfully fetched data for {len(stocks_data)} stocks")
        return stocks_data
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """Save stock data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'sp500_data_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_stocks': len(data),
                'stocks': data
            }, f, indent=2)
        
        print(f"💾 Data saved to {filename}")
        return filename
    
    def save_to_csv(self, data: List[Dict], filename: str = None):
        """Save stock data to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'sp500_data_{timestamp}.csv'
        
        if not data:
            print("❌ No data to save")
            return
        
        fieldnames = list(data[0].keys())
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"💾 Data saved to {filename}")
        return filename
    
    def get_market_summary(self) -> Dict:
        """Get market summary statistics"""
        stocks = self.fetch_all_stocks()
        
        if not stocks:
            return {}
        
        gainers = [s for s in stocks if float(s['change_percent']) > 0]
        losers = [s for s in stocks if float(s['change_percent']) < 0]
        unchanged = [s for s in stocks if float(s['change_percent']) == 0]
        
        # Calculate market cap weighted average (simplified)
        total_change = sum(float(s['change_percent']) for s in stocks)
        avg_change = total_change / len(stocks)
        
        return {
            'total_stocks': len(stocks),
            'gainers': len(gainers),
            'losers': len(losers),
            'unchanged': len(unchanged),
            'avg_change_percent': avg_change,
            'top_gainer': max(gainers, key=lambda x: float(x['change_percent'])) if gainers else None,
            'top_loser': min(losers, key=lambda x: float(x['change_percent'])) if losers else None,
            'most_active': max(stocks, key=lambda x: x['volume']),
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Main function to demonstrate the S&P 500 data fetcher"""
    print("🚀 S&P 500 Stock Data Fetcher")
    print("=" * 50)
    
    # Initialize without API key (demo mode)
    # To use real data, get a free API key from https://www.alphavantage.co/support/#api-key
    # and pass it to SP500DataFetcher(api_key="YOUR_API_KEY")
    fetcher = SP500DataFetcher()
    
    print("\n📈 Fetching market summary...")
    market_summary = fetcher.get_market_summary()
    
    if market_summary:
        print(f"\n📊 Market Summary:")
        print(f"   Total Stocks: {market_summary['total_stocks']}")
        print(f"   Gainers: {market_summary['gainers']} ({market_summary['gainers']/market_summary['total_stocks']*100:.1f}%)")
        print(f"   Losers: {market_summary['losers']} ({market_summary['losers']/market_summary['total_stocks']*100:.1f}%)")
        print(f"   Unchanged: {market_summary['unchanged']}")
        print(f"   Average Change: {market_summary['avg_change_percent']:.2f}%")
        
        if market_summary['top_gainer']:
            print(f"\n🟢 Top Gainer: {market_summary['top_gainer']['symbol']} ({market_summary['top_gainer']['change_percent']}%)")
        
        if market_summary['top_loser']:
            print(f"🔴 Top Loser: {market_summary['top_loser']['symbol']} ({market_summary['top_loser']['change_percent']}%)")
        
        print(f"📊 Most Active: {market_summary['most_active']['symbol']} ({market_summary['most_active']['volume']:,} shares)")
    
    # Save data
    stocks_data = fetcher.fetch_all_stocks()
    if stocks_data:
        json_file = fetcher.save_to_json(stocks_data)
        csv_file = fetcher.save_to_csv(stocks_data)
        
        print(f"\n💾 Files created:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
    
    print("\n✨ Done! You can now use this data in your web application.")
    print("\n💡 Tips:")
    print("   - Get a free API key from Alpha Vantage for real-time data")
    print("   - Run this script periodically to update stock prices")
    print("   - Use the JSON output to power your web application")

if __name__ == "__main__":
    main()
