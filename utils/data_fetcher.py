import pandas as pd
import logging
from typing import Optional, List
from .data_providers import CoinGeckoProvider, YahooFinanceProvider
from config.api_keys import COINGECKO_API_KEY

class CryptoDataFetcher:
    def __init__(self):
        self.providers = []
        self._initialize_providers()
        self.current_provider_index = 0

    def _initialize_providers(self):
        # Initialize CoinGecko provider
        coingecko = CoinGeckoProvider()
        if COINGECKO_API_KEY:
            coingecko.set_api_key(COINGECKO_API_KEY)
        self.providers.append(coingecko)

        # Initialize Yahoo Finance provider
        self.providers.append(YahooFinanceProvider())

    def _get_next_provider(self):
        """Rotate to next available provider"""
        attempts = 0
        while attempts < len(self.providers):
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
            provider = self.providers[self.current_provider_index]
            if not provider.is_rate_limited():
                return provider
            attempts += 1
        return None

    def get_historical_data(self, coin_id: str, timeframe: str) -> pd.DataFrame:
        """
        Fetch historical data using available providers.
        Falls back to alternative providers if one is rate limited.
        """
        for _ in range(len(self.providers)):
            provider = self.providers[self.current_provider_index]

            if provider.is_rate_limited():
                logging.warning(f"{provider.name} is rate limited, trying next provider")
                provider = self._get_next_provider()
                if not provider:
                    logging.error("All providers are rate limited")
                    return pd.DataFrame()

            df = provider.get_historical_data(coin_id, timeframe)
            if not df.empty:
                logging.info(f"Data fetched successfully from {provider.name}")
                return df

            provider = self._get_next_provider()
            if not provider:
                break

        logging.error("Failed to fetch data from all providers")
        return pd.DataFrame()

    def get_supported_timeframes(self) -> List[str]:
        """Get intersection of supported timeframes across all providers"""
        timeframes = set(self.providers[0].get_supported_timeframes())
        for provider in self.providers[1:]:
            timeframes.intersection_update(provider.get_supported_timeframes())
        return sorted(list(timeframes))