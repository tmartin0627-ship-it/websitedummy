# S&P 500 Stock Prices Website

A comprehensive web application that displays real-time stock prices for S&P 500 companies with an elegant, professional interface.

![S&P 500 Stock Tracker](https://img.shields.io/badge/Status-Active-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow) ![HTML5](https://img.shields.io/badge/HTML5-CSS3-orange)

## 🚀 Features

### 📈 Live Stock Data
- Real-time price updates for top S&P 500 companies
- Price changes with color-coded indicators (green for gains, red for losses)
- Volume, market cap, P/E ratios, and 52-week ranges
- Auto-refresh every 30 seconds

### 🎨 Modern Interface
- Dark theme with gradient backgrounds
- Responsive grid layout for stock cards
- Smooth animations and hover effects
- Mobile-friendly design

### 🔍 Advanced Filtering
- Search by company name or stock symbol
- Filter by top gainers, losers, or most active stocks
- Pagination for large datasets
- Real-time filtering without page reloads

### 📊 Market Summary
- Live market indices (S&P 500, NASDAQ, DOW)
- Market statistics (gainers vs losers count)
- Last update timestamp

### 🛠️ API Integration
- RESTful API endpoints for stock data
- Support for real-time data via Alpha Vantage API
- Fallback demo data when API is unavailable

## 🏗️ Project Structure

```
📦 S&P 500 Stock Tracker
├── 📄 sp500_stocks.html          # Main website (frontend)
├── 🐍 sp500_fetcher.py           # Stock data fetcher (backend)
├── 🌐 sp500_server.py            # Flask web server
├── 📋 requirements.txt           # Python dependencies
└── 📖 README.md                  # This file
```

## 🚀 Quick Start

### Option 1: Simple HTML Website (No Backend)
Just open the HTML file directly in your browser:

```bash
# Open the website directly
open sp500_stocks.html
```

The website will display with demo data and full functionality.

### Option 2: Full Web Server with API (Recommended)

1. **Install Python Dependencies**
   ```bash
   # Install required packages
   pip install -r requirements.txt
   ```

2. **Start the Web Server**
   ```bash
   # Run the Flask server
   python sp500_server.py
   ```

3. **Open in Browser**
   ```
   http://localhost:5000
   ```

### Option 3: Real-Time Data with API Key

1. **Get a Free API Key**
   - Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - Sign up for a free account
   - Get your API key

2. **Update the Code**
   ```python
   # In sp500_server.py, replace this line:
   stock_fetcher = SP500DataFetcher()
   
   # With:
   stock_fetcher = SP500DataFetcher(api_key="YOUR_API_KEY_HERE")
   ```

3. **Run with Real Data**
   ```bash
   python sp500_server.py
   ```

## 🔧 API Endpoints

The Flask server provides several API endpoints:

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /` | Main website | `http://localhost:5000` |
| `GET /api/stocks` | All stock data | `http://localhost:5000/api/stocks` |
| `GET /api/stock/<symbol>` | Single stock | `http://localhost:5000/api/stock/AAPL` |
| `GET /api/market-summary` | Market overview | `http://localhost:5000/api/market-summary` |
| `GET /api/gainers` | Top gaining stocks | `http://localhost:5000/api/gainers` |
| `GET /api/losers` | Top losing stocks | `http://localhost:5000/api/losers` |
| `GET /api/most-active` | Most active stocks | `http://localhost:5000/api/most-active` |
| `GET /health` | Health check | `http://localhost:5000/health` |

### Example API Response

```json
{
  "success": true,
  "timestamp": "2025-08-02T10:30:00",
  "stock": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "price": 175.43,
    "change": 2.15,
    "change_percent": "1.24",
    "volume": 45623000,
    "sector": "Technology"
  }
}
```

## 🎯 Features in Detail

### Stock Cards
Each stock is displayed in a beautiful card showing:
- **Company Symbol & Name** - Easy identification
- **Current Price** - Real-time pricing
- **Change Indicator** - Price change with arrow and percentage
- **Volume** - Trading volume formatted (e.g., "45.6M")
- **Market Cap** - Company valuation
- **P/E Ratio** - Price-to-earnings ratio
- **52W Range** - Annual high and low prices

### Search & Filter
- **Live Search** - Type to filter by symbol or company name
- **Category Filters**:
  - All Stocks - Complete S&P 500 list
  - Top Gainers - Best performing stocks
  - Top Losers - Worst performing stocks
  - Most Active - Highest trading volume

### Market Summary Bar
Displays key market statistics:
- Total number of stocks tracked
- Count of gainers, losers, and unchanged stocks
- Last update timestamp

## 🛠️ Customization

### Adding New Stocks
Edit `sp500_fetcher.py` and add symbols to the `load_sp500_symbols()` method:

```python
def load_sp500_symbols(self) -> List[str]:
    return [
        'AAPL', 'MSFT', 'AMZN',  # existing symbols
        'YOUR_SYMBOL_HERE'        # add new symbols
    ]
```

### Styling Changes
Modify the CSS in `sp500_stocks.html` to customize:
- Colors and themes
- Card layouts
- Animations
- Typography

### Data Sources
The app supports multiple data sources:
- **Alpha Vantage API** - Real-time data (requires free API key)
- **Demo Data** - Realistic sample data for testing
- **Local JSON** - Load from saved data files

## 📱 Mobile Support

The website is fully responsive and works great on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Desktop computers
- 🖥️ Large displays

## 🔒 Security Features

- **CORS Enabled** - Cross-origin requests supported
- **Error Handling** - Graceful degradation when APIs fail
- **Rate Limiting** - Built-in API rate limiting
- **Input Validation** - Search input sanitization

## 🐛 Troubleshooting

### Common Issues

**1. "No API key provided" Warning**
- This is normal in demo mode
- Get a free API key from Alpha Vantage for real data

**2. "API limit reached" Messages**
- Free API keys have rate limits
- Demo data will be used automatically

**3. Stock Cards Not Loading**
- Check your internet connection
- Ensure the server is running (if using Flask)
- Check browser console for errors

**4. Server Won't Start**
- Install dependencies: `pip install -r requirements.txt`
- Check if port 5000 is available
- Try a different port: `app.run(port=5001)`

## 📈 Performance

- **Fast Loading** - Optimized for quick page loads
- **Efficient Updates** - Only updates changed data
- **Caching** - Smart caching of API responses
- **Pagination** - Handles large datasets efficiently

## 🤝 Contributing

Feel free to contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Credits

- **Stock Data**: Alpha Vantage API
- **Icons**: Unicode emojis
- **Fonts**: System fonts for best performance
- **Design**: Custom CSS with modern web standards

## 🔮 Future Enhancements

Planned features for future versions:
- 📊 Interactive charts and graphs
- 📈 Historical price data
- 🔔 Price alert notifications
- 💼 Portfolio tracking
- 📊 Technical indicators
- 🌙 Light/dark theme toggle
- 📱 Progressive Web App (PWA) support

---

**Made with ❤️ for stock market enthusiasts**

*Last updated: August 2, 2025*
