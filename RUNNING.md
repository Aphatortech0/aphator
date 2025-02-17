# How to Run Crypto Analysis Bot

## Setup Instructions

1. **Starting the Application**
   - Click the "Run" button in Replit
   - Wait for the application to initialize (this may take a few moments)
   - The app will automatically open in a new window

2. **System Requirements**
   All dependencies are automatically installed by Replit:
   - Python 3.11+
   - Required packages (automatically installed):
     - streamlit
     - pandas
     - plotly
     - tensorflow
     - yfinance
     - scikit-learn
     - numpy

## Using the Application

1. **Basic Navigation**
   - Select cryptocurrency from the dropdown (BTC, ETH, SOL, etc.)
   - Choose timeframe (1m, 3m, 5m, 15m, 30m, 1h, 1d)
   - Adjust chart settings in "Advanced Chart Settings"

2. **Reading the Charts**
   - Main price chart shows candlesticks or line chart
   - Green triangles (↑) indicate "BUY HERE" signals
   - Red triangles (↓) indicate "SELL HERE" signals
   - Moving averages: 20 (orange), 50 (blue), 200 (purple)
   - Bollinger Bands shown as gray dashed lines

3. **Trading Guidance**
   - Click the "🎯 Trading Guidance" expander in sidebar
   - View current market conditions
   - Check price targets and stop losses
   - Review trading recommendations

4. **Technical Indicators**
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Volume analysis
   - Signal strength and confidence levels

5. **Performance Metrics**
   - Total Return
   - Win Rate
   - Maximum Drawdown
   - Number of trades

## Troubleshooting

1. **If charts don't load:**
   - Check your internet connection
   - Refresh the page
   - Try a different timeframe

2. **If data is delayed:**
   - This is normal due to API rate limits
   - Wait a few seconds for refresh
   - Check the "Last updated" timestamp

3. **For technical support:**
   - Contact: aphator@gmail.com
   - Include error messages if any
   - Specify the cryptocurrency and timeframe used

## Important Notes

- The application automatically updates every second
- Trading signals are for informational purposes only
- Always conduct your own research before trading
- Past performance doesn't guarantee future results
