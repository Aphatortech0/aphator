
# Crypto Analysis Bot - User Instructions

## Quick Start on Replit (Recommended)
1. Click the "Run" button in Replit
2. Wait for application initialization
3. Access the interface through the provided URL
4. Select cryptocurrency and timeframe from sidebar
5. Monitor signals and analysis in real-time

## Alternative: Running the Code
1. Install Python 3.11 or higher
2. Install required packages:
```bash
pip install pandas plotly requests scikit-learn streamlit tensorflow trafilatura yfinance
```
3. Run the application:
```bash
streamlit run app.py --server.port 5000
```
4. Open your browser and navigate to `http://0.0.0.0:5000`

## Features
- Live price tracking
- Technical analysis indicators
- AI-powered price predictions
- Trading signals with confidence levels
- Backtesting capabilities
- Interactive charts
- Multiple timeframe support (1m, 3m, 5m, 15m, 30m, 1h, 1d)
- Support for major cryptocurrencies (BTC, ETH, SOL, TON, etc.)

## Usage Guide

### Basic Navigation
1. **Sidebar Controls**
   - Cryptocurrency selection
   - Timeframe selection
   - Chart type and indicator settings

2. **Main Dashboard**
   - Price chart with indicators
   - Current price and predictions
   - Signal strength indicator
   - Technical analysis metrics

3. **Chart Interactions**
   - Zoom: Mouse wheel
   - Pan: Click and drag
   - Reset: Double click
   - Tooltip: Hover over data points
   - Click on "BUY HERE" signals for detailed guidance

### Trading Signals
- **Green Triangle Up**: Buy signal with "BUY HERE" text
- **Red Triangle Down**: Sell signal with "SELL HERE" text
- **Signal Strength**: 0-100%
- **Confidence Level**: Low/Medium/High

### Technical Indicators
- **Moving Averages**: Orange (20), Blue (50), Purple (200)
- **Bollinger Bands**: Gray dashed lines
- **RSI**: 0-100 scale
- **MACD**: Histogram and signal lines

## Support
For technical issues or questions:
1. Check error messages in console
2. Review documentation
3. Contact support: aphator@gmail.com

## Disclaimer
This tool is for informational purposes only. Always conduct thorough research and consider risks before making investment decisions.
"# aphatot" 
