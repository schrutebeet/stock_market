"""
OBJECTIVE OF THIS MODULE
------------------------
Define funtions for fetching data from AlphaVantage API
"""
import pandas as pd
import requests

from dependencies import authenticator


class Stock:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol
        self.api_key = authenticator.api_key

    def fetch_intraday(self, start_date=None, end_date=None):
        """
        Both start and end dates are both inclusive. Must
        follow the YYYY-MM-DD format. If start/end dates
        are not required, do not assign any values to them.
        """
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
            f"&symbol={self.stock_symbol}&outputsize=full&interval=1min&apikey={self.api_key}"
        )
        r = requests.get(url)
        json_data = r.json()["Time Series (1min)"]
        df = pd.DataFrame(json_data).T
        df.index = pd.to_datetime(df.index)

        if start_date is not None:
            start_date = pd.to_datetime(f"{start_date} 00:00:00")
            df = df[df.index >= start_date]
        if end_date is not None:
            end_date = pd.to_datetime(f"{end_date} 23:59:59")
            df = df[df.index <= end_date]

        df.columns = ["open", "high", "low", "close", "volume"]
        return df

    def fetch_daily(self, start_date=None, end_date=None):
        """
        Both start and end dates are both inclusive. Must
        follow the YYYY-MM-DD format. If start/end dates
        are not required, do not assign any values to them.
        """
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED"
            f"&symbol={self.stock_symbol}&outputsize=full&apikey={self.api_key}"
        )
        r = requests.get(url)
        json_data = r.json()["Time Series (Daily)"]
        df = pd.DataFrame(json_data).T.sort_index()
        df.index = pd.to_datetime(df.index)

        if start_date is not None:
            start_date = pd.to_datetime(f"{start_date} 00:00:00")
            df = df[df.index >= start_date]
        if end_date is not None:
            end_date = pd.to_datetime(f"{end_date} 23:59:59")
            df = df[df.index <= end_date]

        df.columns = [
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
            "dividend_amount",
            "split_coeff",
        ]
        return df
