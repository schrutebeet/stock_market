from utils.log_config import logger 
from datetime import datetime, timedelta
from typing import Dict, Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from src.data_extractor.base_extractor import BaseExtractor
from utils.error_handling import ValueOutOfBoundsException, APIError


class StockExtractor(BaseExtractor):
    """Extract stock rates from the AlphaVantage API."""

    ACCEPTABLE_PERIODS = ["1min", "5min", "15min", "30min", "60min", "daily"]

    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
        self.url = None

    def get_data(self, 
                 period: str = "daily", 
                 from_date: str = (datetime.now()  - timedelta(days=1)).strftime("%Y-%m-%d"), 
                 until_date: str =(datetime.now()  - timedelta(days=1)).strftime("%Y-%m-%d")) -> pd.DataFrame:
        """Get the stock data from the API for a specified symbol.

        Args:
            period (str, optional): Defines the window size for each new quote. Defaults to "daily".
            from_date (str, optional): Date from where to start fetching data. Only accepts '%Y-m-%d' string formats. 
                                       Defaults to datetime.now().strftime("%Y-%m-%d") - timedelta(days=1) (yesterday).
            until_date (str, optional): Date from where to end fetching data. Only accepts '%Y-m-%d' string formats. 
                                        Defaults to datetime.now().strftime("%Y-%m-%d") - timedelta(days=1) (yesterday).

        Raises:
            ValueOutOfBoundsException: Raises exception if the 'period' argument is not within the 
                                       default values from the 'ACCEPTABLE_PERIODS' class attribute.

        Returns:
            pd.DataFrame: Returns DataFrame containing OHLCV information.
        """
        logger.info(f"Extracting {period} stock information for {self.symbol}.")
        if period not in self.ACCEPTABLE_PERIODS:
            raise ValueOutOfBoundsException(
                f"Argument 'period' must be one of these categories: \
                                            {', '.join(self.ACCEPTABLE_PERIODS)}"
            )

        json_rates = {}
        current_month = datetime.strptime(from_date, "%Y-%m-%d").replace(day=1)
        last_month = datetime.strptime(until_date, "%Y-%m-%d").replace(day=1)
        while current_month <= last_month:
            month_str = current_month.strftime("%Y-%m")
            new_data = self.__choose_function_type(period, month_str)
            json_rates.update(new_data)
            logger.info(
                f"{self.symbol}: Extracting information for month {month_str}"
            )
            current_month += relativedelta(months=1)
        df = pd.DataFrame(json_rates).T
        if period == "daily":
            renamed_cols = {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. adjusted close": "adj_close",
                "6. volume": "volume",
                "7. dividend amount": "dividend_amount",
                "8. split coefficient": "split_coeff",
            }
        else:
            renamed_cols = {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. volume": "volume",
            }
        df = df.rename(columns=renamed_cols)
        df.index = pd.to_datetime(df.index)

        # Apply specific daydate filters
        start_date = pd.to_datetime(f"{from_date} 00:00:00")
        end_date = pd.to_datetime(f"{until_date} 23:59:59")
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.fillna(method="ffill")
        df['datetime'] = df.index
        df['timestamp'] = datetime.utcnow()
        df['symbol'] = self.symbol

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
        if period == "daily":
            self.url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="
                f"{self.symbol}&outputsize=full&apikey={self.api_key}"
            )
            response = self.__return_request(self.url)
            json_data = response["Time Series (Daily)"]
        else:
            self.url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="
                f"{self.symbol}&outputsize=full&month={month}&interval={period}&apikey={self.api_key}"
            )
            response = self.__return_request(self.url)
            json_data = response[f"Time Series ({period})"]

        return json_data

    @staticmethod
    def __return_request(url: str) -> dict:
        """_summary_

        Args:
            url (str): Endpoint url for the API call.

        Raises:
            APIError: Raise custom error if any problem arises within the API. 

        Returns:
            dict: Returns a dictionary with the stated characteristics.
        """
        try:
            r = requests.get(url)
            r_json = r.json()
            if len(r_json) == 0:
                logger.error(f"API response returned an empty dictionary")
                raise APIError
            
            potential_error_message = list(r_json.keys())[0]
            potential_error_explanation = list(r_json.values())[0]
            if potential_error_message.lower() == "error message":
                logger.error(f"{potential_error_explanation}")
                raise APIError

        except requests.exceptions.RequestException:
            logger.error(f"Could not connect with AlphaVantage API. Please, "\
                           "make sure you are connected to the internet")

        return r_json
