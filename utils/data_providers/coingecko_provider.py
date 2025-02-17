import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import logging
from .base_provider import BaseDataProvider

class CoinGeckoProvider(BaseDataProvider):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.min_request_interval = 30  # 30 seconds between requests

    def _get_timeframe_params(self, timeframe):
        mapping = {
            "1m": {"days": "1", "interval": "minutely"},
            "5m": {"days": "1", "interval": "minutely"},
            "15m": {"days": "1", "interval": "minutely"},
            "30m": {"days": "1", "interval": "minutely"},
            "1h": {"days": "1", "interval": "hourly"},
            "4h": {"days": "7", "interval": "hourly"},
            "1d": {"days": "30", "interval": "daily"},
            "7d": {"days": "90", "interval": "daily"},
            "30d": {"days": "365", "interval": "daily"}
        }
        return mapping.get(timeframe, {"days": "30", "interval": "daily"})

    def get_supported_timeframes(self):
        return ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "7d", "30d"]

    def is_rate_limited(self):
        current_time = time.time()
        if current_time - self.last_request_time < self.min_request_interval:
            return True
        return self.rate_limited

    def get_historical_data(self, coin_id: str, timeframe: str) -> pd.DataFrame:
        try:
            cache_key = f"{coin_id}_{timeframe}"
            current_time = time.time()

            # Check cache
            if cache_key in self.cache:
                data, timestamp = self.cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    return data

            # Check rate limit
            if self.is_rate_limited():
                logging.warning("CoinGecko rate limited, returning cached data")
                return self.cache.get(cache_key, (pd.DataFrame(), 0))[0]

            params = self._get_timeframe_params(timeframe)
            url = f"{self.base_url}/coins/{coin_id}/market_chart"

            headers = {}
            if hasattr(self, 'api_key') and self.api_key:
                headers['x-cg-pro-api-key'] = self.api_key

            response = requests.get(url, params={
                "vs_currency": "usd",
                "days": params["days"],
                "interval": params["interval"]
            }, headers=headers)

            if response.status_code == 429:
                self.rate_limited = True
                return self.cache.get(cache_key, (pd.DataFrame(), 0))[0]

            response.raise_for_status()
            self.last_request_time = current_time
            self.rate_limited = False

            data = response.json()
            df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

            # Process data based on timeframe
            df = self._process_dataframe(df, timeframe)
            
            # Cache results
            self.cache[cache_key] = (df, current_time)
            return df

        except Exception as e:
            logging.error(f"CoinGecko error: {str(e)}")
            return pd.DataFrame()

    def _process_dataframe(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        resample_map = {
            "1m": "1min", "5m": "5min", "15m": "15min",
            "30m": "30min", "1h": "1H", "4h": "4H", "1d": "1D"
        }

        if timeframe in resample_map:
            rule = resample_map[timeframe]
            df = df.resample(rule).agg({
                "price": "ohlc"
            }).dropna()
            df.columns = ["open", "high", "low", "close"]
        else:
            df["open"] = df["price"]
            df["high"] = df["price"]
            df["low"] = df["price"]
            df["close"] = df["price"]

        df["volume"] = df["close"].rolling(window=2).std().fillna(0)
        df["Price_Change"] = df["close"].pct_change()

        return df
