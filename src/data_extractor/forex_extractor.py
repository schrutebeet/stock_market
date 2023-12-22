from config.log_config import logger 
from datetime import datetime
from typing import Dict

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from src.data_extractor.base_extractor import BaseExtractor
from utils.error_handling import ValueOutOfBoundsException, APIError


class ForexExtractor(BaseExtractor):
    """Extract forex rates from the AlphaVantage API."""

    ACCEPTABLE_PERIODS = ["1min", "5min", "15min", "30min", "60min", "daily"]

    def __init__(self, symbol_pair: str):
        """Class initializer.

        Args:
            symbol_pair (str): Pair from where to fetch data. Argument value must be of the form "FX1/FX"".
                               For example, "EUR/USD" or "NOK/CHF". first one is the element to be converted
                               to the second element. 
        """
        super().__init__()
        self.symbol_pair = symbol_pair
        self.from_symbol = symbol_pair.split('/')[0]
        self.to_symbol = symbol_pair.split('/')[1]
        self.url = None

    def get_data(self, 
                 period: str = "daily", 
                 from_date: str = datetime.now().strftime("%Y-%m-%d"), 
                 until_date: str = datetime.now().strftime("%Y-%m-%d")) -> pd.DataFrame:
        """Get the FOREX data from the API for a specified symbol.

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
            logger.error(f"Argument 'period' must be one of these categories: " \
                                            f"{', '.join(self.ACCEPTABLE_PERIODS)}")
            raise ValueOutOfBoundsException

        new_data = self.__choose_function_type(period)
        df = pd.DataFrame(new_data).T
        if period == "daily":
            renamed_cols = {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
            }
            df = df.rename(columns=renamed_cols)
        else:
            renamed_cols = {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
            }
            df = df.rename(columns=renamed_cols)
        df.index = pd.to_datetime(df.index)

        # Apply specific daydate filters
        start_date = pd.to_datetime(f"{from_date} 00:00:00")
        end_date = pd.to_datetime(f"{until_date} 23:59:59")
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.fillna(method="ffill")
        df['symbol_pair'] = self.symbol_pair
        if start_date < min(df.index):
            logger.warning(f"API could not provide quotes on all days. It was asked to "\
                            f"provide data from {start_date} but could only provide from {str(min(df.index))}")

        return df

    def __choose_function_type(self, period: str) -> Dict[str, str]:
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
                f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={self.from_symbol}"\
                f"&to_symbol={self.to_symbol}&apikey={self.api_key}"
            )
            response = self.__return_request(self.url)
            json_data = response["Time Series FX (Daily)"]
        else:
            self.url = (
                f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={self.from_symbol}"\
                f"&to_symbol={self.to_symbol}&interval={period}&outputsize=full"\
                f"&apikey={self.api_key}"
            )
            response = self.__return_request(self.url)
            json_data = response[f"Time Series FX ({period})"]

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
