import pandas as pd
import yfinance as yf
import logging
import time
from datetime import datetime, timedelta
from .base_provider import BaseDataProvider

class YahooFinanceProvider(BaseDataProvider):
    def __init__(self):
        super().__init__()
        self.cache = {}
        self.cache_timeout = 300
        self.min_request_interval = 5  # Yahoo has more lenient rate limits
        self.symbol_map = {
            'btc': 'BTC-USD',
            'eth': 'ETH-USD',
            'sol': 'SOL-USD',
            'ton': 'TONCOIN-USD',
            'ada': 'ADA-USD',
            'dot': 'DOT-USD',
            'link': 'LINK-USD',
            'matic': 'MATIC-USD',
            'doge': 'DOGE-USD',
            'shib': 'SHIB-USD',
            'avax': 'AVAX-USD',
            'uni': 'UNI-USD',
            'xrp': 'XRP-USD'
        }

    def get_supported_timeframes(self):
        return ["1m", "3m", "5m", "15m", "30m", "1h", "1d"]

    def is_rate_limited(self):
        current_time = time.time()
        return (current_time - self.last_request_time) < self.min_request_interval

    def get_supported_coins(self):
        return list(self.symbol_map.keys())

    def get_historical_data(self, coin_id: str, timeframe: str) -> pd.DataFrame:
        try:
            cache_key = f"{coin_id}_{timeframe}"
            current_time = time.time()

            if cache_key in self.cache:
                data, timestamp = self.cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    return data

            if self.is_rate_limited():
                return self.cache.get(cache_key, (pd.DataFrame(), 0))[0]

            symbol = self.symbol_map.get(coin_id.lower())
            if not symbol:
                logging.error(f"Unsupported coin: {coin_id}")
                return pd.DataFrame()

            interval_map = {
                "1m": "1m",
                "3m": "3m",
                "5m": "5m",
                "15m": "15m",
                "30m": "30m",
                "1h": "1h",
                "1d": "1d"
            }

            period_map = {
                "1m": "1d",
                "3m": "1d",
                "5m": "1d",
                "15m": "1d",
                "30m": "5d",
                "1h": "7d",
                "1d": "60d"
            }

            interval = interval_map.get(timeframe, "1h")
            period = period_map.get(timeframe, "7d")

            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                return pd.DataFrame()

            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            df["Price_Change"] = df["close"].pct_change()

            self.cache[cache_key] = (df, current_time)
            self.last_request_time = current_time

            return df

        except Exception as e:
            logging.error(f"Yahoo Finance error: {str(e)}")
            return pd.DataFrame()