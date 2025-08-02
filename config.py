"""
Configuration file for S&P 500 Stock Tracker
Store your API keys and settings here
"""

# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY = "CV9XIR3ZT6QOTDAT"

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
DEBUG_MODE = True

# Data Configuration
DEFAULT_STOCKS_PER_PAGE = 20
AUTO_REFRESH_INTERVAL = 30  # seconds
API_RATE_LIMIT_DELAY = 12   # seconds between API calls (Alpha Vantage free tier allows 5 calls per minute)

# Cache Configuration
CACHE_DURATION = 300  # 5 minutes in seconds
