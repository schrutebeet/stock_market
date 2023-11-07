import logging
from datetime import datetime
from typing import Dict, Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from dependencies import authenticator
from utils.error_handling import ValueOutOfBoundsException


class StocksExtractor(BaseExtractor):
    """Extract rates from the AlphaVantage API."""

    ACCEPTABLE_PERIODS = ["1min", "5min", "15min", "30min", "60min", "1min", "daily"]

    def __init__(self, symbol: str, api_key: Any, function: str):
        super().__init__(symbol, api_key, function)

    def get_stock_data(self, period: str = "daily", full_data: bool = False) -> pd.DataFrame:
        """Get the stock data from the API for a specified symbol.

        Args:
            period (str, optional): Defines the window size for each new quote. Defaults to "daily".
            full_data (bool, optional): If set to True, provides full data since the year 2000. 
                                        Otherwise, it provides data only for the current month. 
                                        Defaults to False.

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

        if full_data:
            json_rates = {}
            start_date = datetime(2000, 1, 1)
            current_date = datetime.now()
            current_month = start_date
            while current_month <= current_date:
                month_str = current_month.strftime("%Y-%m")
                new_data = self.__choose_function_type(period, month_str)
                json_rates.update(new_data)
                logging.info(
                    f"Extracting months from {start_date.strftime('%Y-%m')}" f"until {current_date.strftime('%Y-%m')}"
                )
                current_month += relativedelta(months=1)
        else:
            json_rates = self.__choose_function_type(period)

        df = pd.DataFrame(json_rates).T
        if period != "daily":
            df.columns = ["open", "high", "low", "close", "volume"]
        else:
            df.columns = ["open","high", "low", "close", "adj_close", 
                          "volume", "dividend_amount", "split_coeff"]
        df.index = pd.to_datetime(df.index)

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
