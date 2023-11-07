import logging
from datetime import datetime
from typing import Dict, Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from src.data_extractor.base_extractor import BaseExtractor
from utils.error_handling import ValueOutOfBoundsException


class StocksExtractor(BaseExtractor):
    """Extract stock rates from the AlphaVantage API."""

    ACCEPTABLE_PERIODS = ["1min", "5min", "15min", "30min", "60min", "daily"]

    def __init__(self, symbol: str, api_key: Any, function: str):
        super().__init__(symbol, api_key, function)

    def get_data(self, 
                 period: str = "daily", 
                 from_date: str = datetime.now().strftime("%Y-%m-%d"), 
                 until_date: str = datetime.now().strftime("%Y-%m-%d")) -> pd.DataFrame:
        """Get the stock data from the API for a specified symbol.

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
            df.columns = ["open", "high", "low", "close", "volume"]
        else:
            df.columns = ["open","high", "low", "close", "adj_close", 
                          "volume", "dividend_amount", "split_coeff"]
        df.index = pd.to_datetime(df.index)

        # Apply specific daydate filters
        start_date = pd.to_datetime(f"{from_date} 00:00:00")
        end_date = pd.to_datetime(f"{until_date} 23:59:59")
        df = df[(df.index >= start_date) & (df.index <= end_date)]

        return df

    def __choose_function_type(self, period: str, month: str = datetime.now().strftime("%Y-%m")) -> Dict[str, str]:
        """Decide wich endpoint to trigger depending on the period category.

        Args:
            period (str): Defines the window size for each new quote. Defaults to "daily".
            month (str, optional): Timespan of the extracted information. 
                                   Defaults to datetime.now().strftime("%Y-%m").

        Returns:
            Dict[str, str]: JSON file containing OHLCV information from the API.
        """
        if period != "daily":
            present_month = datetime.now().strftime("%Y-%m")
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="
                f"{self.symbol}&month={present_month}&interval={period}&apikey={self.api_key}"
            )
            r = requests.get(url)
            json_data = r.json()[f"Time Series {period}"]
        else:
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="
                f"{self.symbol}&interval={period}&apikey={self.api_key}"
            )
            r = requests.get(url)
            json_data = r.json()["Time Series (Daily)"]

            return json_data
