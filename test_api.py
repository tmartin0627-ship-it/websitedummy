#!/usr/bin/env python3
"""
Quick test script to verify Alpha Vantage API key is working
"""

import requests
import json
from datetime import datetime

def test_api_key(api_key, symbol="AAPL"):
    """Test the Alpha Vantage API key with a single stock request"""
    
    print(f"🔑 Testing Alpha Vantage API key with symbol: {symbol}")
    print("=" * 50)
    
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    
    try:
        print("📡 Making API request...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print("✅ API request successful!")
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            print(f"\n📊 {symbol} Stock Data:")
            print(f"   Symbol: {quote.get('01. symbol', 'N/A')}")
            print(f"   Price: ${quote.get('05. price', 'N/A')}")
            print(f"   Change: {quote.get('09. change', 'N/A')}")
            print(f"   Change %: {quote.get('10. change percent', 'N/A')}")
            print(f"   Volume: {quote.get('06. volume', 'N/A')}")
            print(f"   Last Trading Day: {quote.get('07. latest trading day', 'N/A')}")
            
            return True
            
        elif 'Note' in data:
            print("⚠️  API Rate Limit Notice:")
            print(f"   {data['Note']}")
            return False
            
        elif 'Error Message' in data:
            print("❌ API Error:")
            print(f"   {data['Error Message']}")
            return False
            
        else:
            print("⚠️  Unexpected response format:")
            print(json.dumps(data, indent=2))
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Your Alpha Vantage API key
    API_KEY = "CV9XIR3ZT6QOTDAT"
    
    print("🚀 Alpha Vantage API Key Test")
    print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test with Apple stock
    success = test_api_key(API_KEY, "AAPL")
    
    if success:
        print("\n🎉 API key is working perfectly!")
        print("✅ Your S&P 500 website will now display real-time data")
    else:
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check if your API key is correct")
        print("   2. Ensure you haven't exceeded the rate limit (5 calls/minute)")
        print("   3. Verify your internet connection")
        print("   4. The website will use demo data as fallback")
    
    print("\n🌐 Visit your website at: http://localhost:5000")
