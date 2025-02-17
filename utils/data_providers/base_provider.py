from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict

class BaseDataProvider(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        self.rate_limited = False
        self.last_request_time = 0
        self.min_request_interval = 30  # Default 30 seconds

    @abstractmethod
    def get_historical_data(self, coin_id: str, timeframe: str) -> pd.DataFrame:
        """Fetch historical price data for a given cryptocurrency"""
        pass

    @abstractmethod
    def is_rate_limited(self) -> bool:
        """Check if the provider is currently rate limited"""
        pass

    @abstractmethod
    def get_supported_timeframes(self) -> list:
        """Return list of supported timeframes"""
        pass

    def set_api_key(self, api_key: str) -> None:
        """Set API key if available"""
        self.api_key = api_key
