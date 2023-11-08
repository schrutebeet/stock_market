import logging
from datetime import datetime
from typing import Dict, Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from src.data_extractor.base_extractor import BaseExtractor
from utils.error_handling import ValueOutOfBoundsException


class CryptoExtractor(BaseExtractor):
    """Extract crypto rates from the AlphaVantage API."""

    ACCEPTABLE_PERIODS = ["1min", "5min", "15min", "30min", "60min", "daily"]

    def __init__(self, symbol: str, api_key: Any, function: str):
        super().__init__(symbol, api_key, function)
        self.currency = "USD"

    def get_data(self, 
                 period: str = "daily", 
                 from_date: str = datetime.now().strftime("%Y-%m-%d"), 
                 until_date: str = datetime.now().strftime("%Y-%m-%d")) -> pd.DataFrame:
        """Get the crypto data from the API for a specified symbol.

        Args:
            period (str, optional): Defines the window size for each new quote. Defaults to "daily".
            from_date (str, optional): Date from where to start fetching data. Only accepts '%Y-m-%d'
                                       string formats. Defaults to datetime.now().strftime("%Y-%m-%d")
                                       (today).
            until_date (str, optional): Date from where to end fetching data. Only accepts '%Y-m-%d'
                                        string formats. Defaults to datetime.now().strftime("%Y-%m-%d")
                                        (today).

        Raises:
            ValueOutOfBoundsException: Raises exception if the 'period' argument is not within the 
                                       default values from the 'ACCEPTABLE_PERIODS' class attribute.

        Returns:
            pd.DataFrame: Returns DataFrame containing OHLCV information.
        """
        if period not in self.ACCEPTABLE_PERIODS:
            raise ValueOutOfBoundsException(
                f"Argument 'period' must be one of these categories: \
                                            {', '.join(self.ACCEPTABLE_PERIODS)}"
            )

        json_rates = {}
        current_date = datetime.now()
        current_month = from_date
        while current_month <= until_date:
            month_datetime = datetime.strptime(current_month, "%Y-%m-%d")
            month_str = month_datetime.strftime("%Y-%m")
            new_data = self.__choose_function_type(period, month_str)
            json_rates.update(new_data)
            logging.info(
                f"Extracting stock information for {month_str}"
            )
            current_month += relativedelta(months=1)

        df = pd.DataFrame(json_rates).T
        if period != "daily":
            renamed_cols = {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. volume": "volume",
            }
            df = df.rename(columns=renamed_cols)
            df['currency'] = self.currency
        else:
            renamed_cols = {
                f"1a. open ({self.currency})": f"open_{self.currency}",
                "1b. open (USD)": "open_USD",
                f"2a. high ({self.currency})": f"high_{self.currency}",
                "2b. high (USD)": "high_USD",
                f"3a. low ({self.currency})": f"low_{self.currency}",
                "3b. low (USD)": "low_USD",
                f"4a. close ({self.currency})": f"close_{self.currency}",
                "4b. close (USD)": "close_USD",
                f"5a. volume ({self.currency})": f"volume_{self.currency}",
                "5b. volume (USD)": "volume_USD",
            }
            df = df.rename(columns=renamed_cols)
        df.index = pd.to_datetime(df.index)

        # Apply specific daydate filters
        start_date = pd.to_datetime(f"{from_date} 00:00:00")
        end_date = pd.to_datetime(f"{until_date} 23:59:59")
        df = df[(df.index >= start_date) & (df.index <= end_date)]

        return df

    def __choose_function_type(self, period: str, month: str) -> Dict[str, str]:
        """Decide wich endpoint to trigger depending on the period category.

        Args:
            period (str): Defines the window size for each new quote. Defaults to "daily".
            month (str, optional): Timespan of the extracted information. 
                                   Defaults to datetime.now().strftime("%Y-%m").

        Returns:
            Dict[str, str]: JSON file containing OHLCV information from the API.
        """
        if period != "daily":
            url = (
                f"https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol="\
                f"{self.symbol}&market={self.self.currency}&interval={period}&outputsize=full"\
                f"&apikey={self.api_key}"
            )
            r = requests.get(url)
            json_data = r.json()[f"Time Series Crypto {period}"]
        else:
            url = (
                f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol="\
                f"{self.symbol}&interval={period}&apikey={self.api_key}"
            )
            r = requests.get(url)
            json_data = r.json()["Time Series (Digital Currency Daily)"]

            return json_data
