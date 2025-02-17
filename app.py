import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.data_fetcher import CryptoDataFetcher
from utils.technical_analysis import TechnicalAnalyzer
from utils.backtester import Backtester
from utils.incremental_learner import IncrementalLearner
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Crypto Analysis Bot", layout="wide")

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'learner' not in st.session_state:
    st.session_state.learner = None
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'candlestick'
if 'show_ma' not in st.session_state:
    st.session_state.show_ma = True
if 'show_bb' not in st.session_state:
    st.session_state.show_bb = True
if 'show_volume' not in st.session_state:
    st.session_state.show_volume = True

def initialize_learner(analyzer):
    if st.session_state.learner is None:
        st.session_state.learner = IncrementalLearner(analyzer.model)
        st.session_state.learner.start()

def show_trading_guidance(price, signal_strength, rsi, macd):
    # Trading guidance container
    with st.sidebar.expander("🎯 Trading Guidance", expanded=True):
        # Current metrics
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Current Price", f"${price:.2f}")
            st.metric("RSI", f"{rsi:.1f}")
        with metrics_col2:
            st.metric("Signal Strength", f"{signal_strength:.1f}%")
            st.metric("MACD", f"{macd:.2f}")

        # Market conditions
        st.markdown("### Market Conditions")
        conditions = []

        # RSI conditions
        if rsi < 30:
            conditions.append("✅ **Oversold** - Strong buy signal")
        elif rsi > 70:
            conditions.append("⚠️ **Overbought** - Consider taking profits")
        else:
            conditions.append("📊 RSI in neutral zone")

        # Signal strength conditions
        if signal_strength > 80:
            conditions.append("💪 **Strong signal** detected")
        elif signal_strength < 40:
            conditions.append("⚠️ Weak signal - Wait for confirmation")

        # MACD conditions
        if macd > 0:
            conditions.append("📈 Positive MACD - Bullish momentum")
        else:
            conditions.append("📉 Negative MACD - Bearish momentum")

        for condition in conditions:
            st.markdown(condition)

        # Price targets
        volatility = 0.05  # Base volatility
        if signal_strength > 70:
            volatility *= 1.5  # Increase targets for strong signals

        st.markdown("### 🎯 Price Targets")
        targets_col1, targets_col2 = st.columns(2)

        with targets_col1:
            st.markdown("**Take Profit**")
            st.markdown(f"""
            🟢 Conservative: ${price * (1 + volatility):.2f} (+{volatility*100:.1f}%)
            🟡 Moderate: ${price * (1 + volatility*1.5):.2f} (+{volatility*150:.1f}%)
            🔵 Aggressive: ${price * (1 + volatility*2):.2f} (+{volatility*200:.1f}%)
            """)

        with targets_col2:
            st.markdown("**Stop Loss**")
            st.markdown(f"""
            🟡 Tight: ${price * (1 - volatility*0.5):.2f} (-{volatility*50:.1f}%)
            🟠 Normal: ${price * (1 - volatility):.2f} (-{volatility*100:.1f}%)
            🔴 Wide: ${price * (1 - volatility*1.5):.2f} (-{volatility*150:.1f}%)
            """)

        # Trading recommendation
        st.markdown("### 📊 Trading Recommendation")
        if signal_strength > 70 and rsi < 60:
            st.success("Strong Buy Signal - Good entry point")
        elif signal_strength > 70 and rsi > 70:
            st.warning("Overbought - Wait for pullback")
        elif signal_strength < 30 and rsi > 40:
            st.error("Consider Taking Profits")
        else:
            st.info("Monitor - No clear signal")


def main():
    st.title("Cryptocurrency Analysis Bot")

    # Get list of supported coins from provider
    data_fetcher = CryptoDataFetcher()
    provider = data_fetcher.providers[1]  # Use Yahoo Finance provider for coin list
    available_coins = provider.get_supported_coins()

    # Sidebar controls
    st.sidebar.header("Configuration")

    # Advanced Settings
    with st.sidebar.expander("Advanced Chart Settings", expanded=False):
        st.session_state.chart_type = st.selectbox(
            "Chart Type",
            ['candlestick', 'line', 'area', 'scatter'],
            index=['candlestick', 'line', 'area', 'scatter'].index(st.session_state.chart_type)
        )

        st.session_state.show_ma = st.checkbox("Show Moving Averages", value=st.session_state.show_ma)
        st.session_state.show_bb = st.checkbox("Show Bollinger Bands", value=st.session_state.show_bb)
        st.session_state.show_volume = st.checkbox("Show Volume", value=st.session_state.show_volume)

        # Color settings
        ma_colors = {
            'MA20': st.color_picker('MA20 Color', '#FF9800'),
            'MA50': st.color_picker('MA50 Color', '#2196F3'),
            'MA200': st.color_picker('MA200 Color', '#9C27B0')
        }

    # Coin and timeframe selection
    coin = st.sidebar.selectbox(
        "Select Cryptocurrency",
        available_coins,
        format_func=lambda x: x.upper()
    )

    try:
        analyzer = TechnicalAnalyzer()
        backtester = Backtester()

        initialize_learner(analyzer)

        # Get supported timeframes from data fetcher
        supported_timeframes = data_fetcher.get_supported_timeframes()
        timeframe = st.sidebar.selectbox(
            "Select Timeframe", 
            supported_timeframes,
            index=min(2, len(supported_timeframes)-1)
        )

        with st.spinner('Fetching latest data...'):
            df = data_fetcher.get_historical_data(coin.lower(), timeframe)

            if df.empty:
                st.error("Unable to fetch data. Please try again in a few minutes (rate limit reached).")
                return

            df = analyzer.calculate_indicators(df)
            signals, prediction = analyzer.generate_signals(df)

            if signals.empty:
                st.error("Unable to generate trading signals.")
                return

            entry_points, exit_points = analyzer.get_entry_exit_points(df, signals)

            # Show trading guidance in sidebar
            if prediction:
                show_trading_guidance(
                    prediction['current_price'],
                    prediction['pattern_confidence'],
                    df['RSI'].iloc[-1],
                    df['MACD'].iloc[-1]
                )

            if len(df) >= 30:
                features = df[['close', 'RSI', 'MACD', 'volume', 'Price_Change']].values[-30:]
                label = df['Price_Change'].iloc[-1]
                st.session_state.learner.add_training_data(features, label)

        st.sidebar.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Main chart
        st.subheader(f"{coin} Price Analysis")
        fig = go.Figure()

        # Base chart based on type
        if st.session_state.chart_type == 'candlestick':
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="Price"
            ))
        elif st.session_state.chart_type == 'line':
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['close'],
                name="Price",
                line=dict(color='#00BCD4')
            ))
        elif st.session_state.chart_type == 'area':
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['close'],
                fill='tonexty',
                name="Price",
                line=dict(color='#00BCD4')
            ))
        else:  # scatter
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['close'],
                mode='markers',
                name="Price",
                marker=dict(color='#00BCD4')
            ))

        # Add technical indicators based on settings
        if st.session_state.show_ma and all(col in df.columns for col in ['MA20', 'MA50', 'MA200']):
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], 
                               name="20 MA", line=dict(color=ma_colors['MA20'])))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], 
                               name="50 MA", line=dict(color=ma_colors['MA50'])))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], 
                               name="200 MA", line=dict(color=ma_colors['MA200'])))

        if st.session_state.show_bb and all(col in df.columns for col in ['BB_upper', 'BB_middle', 'BB_lower']):
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], 
                               name="BB Upper", line=dict(color='gray', dash='dash')))
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], 
                               name="BB Lower", line=dict(color='gray', dash='dash')))

        # Add entry/exit points
        if entry_points:
            fig.add_trace(go.Scatter(
                x=[p['timestamp'] for p in entry_points],
                y=[p['price'] for p in entry_points],
                mode='markers+text',
                name='Buy Signal',
                marker=dict(symbol='triangle-up', size=15, color='green'),
                text=['BUY HERE' for _ in entry_points],
                textposition='top center'
            ))

        if exit_points:
            fig.add_trace(go.Scatter(
                x=[p['timestamp'] for p in exit_points],
                y=[p['price'] for p in exit_points],
                mode='markers+text',
                name='Sell Signal',
                marker=dict(symbol='triangle-down', size=15, color='red'),
                text=['SELL HERE' for _ in exit_points],
                textposition='bottom center',
                textfont=dict(color='red', size=12)
            ))

        # Volume subplot if enabled
        if st.session_state.show_volume:
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volume',
                marker_color='rgba(128,128,128,0.5)',
                yaxis='y2'
            ))

        # Layout updates
        fig.update_layout(
            title=f"{coin} Price Chart with Trading Signals",
            yaxis_title="Price (USD)",
            xaxis_title="Date",
            height=600,
            template='plotly_dark',
            hovermode='x unified',
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False
            ) if st.session_state.show_volume else None
        )

        st.plotly_chart(fig, use_container_width=True)

        # Live Predictions and Signals
        if prediction:
            st.subheader("Live Trading Signals")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Current Price", 
                         f"${prediction['current_price']:.2f}",
                         delta=f"{df['Price_Change'].iloc[-1]*100:.2f}%")

            with col2:
                predicted_change = prediction['predicted_change']
                st.metric("Predicted Change", 
                         f"{predicted_change:.2f}%",
                         delta=f"{predicted_change:.2f}%")

            with col3:
                confidence = prediction['pattern_confidence']
                st.metric("Signal Confidence", 
                         f"{confidence:.1f}%")

            with col4:
                latest_signal = signals['Final_Signal'].iloc[-1]
                signal_color = "green" if latest_signal == "BUY" else "red" if latest_signal == "SELL" else "gray"
                st.markdown(f"<h1 style='text-align: center; color: {signal_color};'>{latest_signal}</h1>", 
                          unsafe_allow_html=True)

            if abs(predicted_change) > 5:
                warning = f"ALERT: Strong {'upward' if predicted_change > 0 else 'downward'} movement expected!"
                st.warning(warning)

        # Technical Analysis Indicators
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("RSI")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI"))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(height=300, template='plotly_dark')
            st.plotly_chart(fig_rsi, use_container_width=True)

        with col2:
            st.subheader("MACD")
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD"))
            if 'MACD_Signal' in df.columns:
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name="Signal"))
            if 'MACD_Hist' in df.columns:
                fig_macd.add_bar(x=df.index, y=df['MACD_Hist'], name="Histogram")
            fig_macd.update_layout(height=300, template='plotly_dark')
            st.plotly_chart(fig_macd, use_container_width=True)

        # Backtesting Results
        st.subheader("Strategy Performance")
        backtest_results = backtester.run_backtest(df, signals)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Return", f"{backtest_results['Total Return']:.2f}%")
        with col2:
            st.metric("Win Rate", f"{backtest_results['Win Rate']*100:.1f}%")
        with col3:
            st.metric("Max Drawdown", f"{backtest_results['Max Drawdown']:.2f}%")

        time.sleep(1)  # 1-second refresh rate
        st.rerun()

    except Exception as e:
        logger.error(f"Error in main app: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try again later or contact support at aphator@gmail.com if the problem persists.")

if __name__ == "__main__":
    main()