from datetime import datetime, timedelta
from typing import Union, Tuple

import pandas as pd
import yfinance as yf

from config.log_config import logger 
from src.data_extractor.base_extractor import BaseExtractor


class StockExtractor(BaseExtractor):
    """Extract stock rates from the AlphaVantage API."""

    VALID_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
        self.url = None

    def get_data(self,
                 end_date: str = datetime.now().strftime('%Y-%m-%d'),
                 lookback_period: int = 30,
                 chunk_size: int = 7,
                 interval: str = "1m")-> pd.DataFrame:
        """Get OHLCV data for any given stock, with a given frequency, with a maximum lookback period of 30 days.

        Args:
            end_date (str): Latest date to compute. Follows the "%Y-%m-%d" format.
            lookback_period (int): Number of days to look back from the end date. Maximum 30 days.
            chunk_size (int): Number of days that each chunk must have.
            interval (str, optional): The interval determines the time span between to consecutive rows in the dataframe.
                                      Defaults to "1d".

        Returns:
            pd.DataFrame: Dataframe with OHLCV data for the given stock.
        """
        df_list = []
        start_dates, end_dates = self.calculate_date_chunks(end_date, lookback_period, chunk_size)
        for start, end in zip(start_dates, end_dates):
            aapl = yf.download(tickers=self.symbol, start=start, end=end, interval=interval)
            df_list.append(aapl)
        df = pd.concat(df_list)
        logger.debug(f"Data on {self.symbol} with {len(df)} rows has been imported successfully.")
        return df

    @staticmethod
    def calculate_date_chunks(end_date: str, lookback_period: int, chunk_size: int) -> Union[Tuple[str]]:
        """Calculate periods of {chunk_size} days according to an end date and a lookback period.

        Args:
            end_date (str): Latest date to compute. Follows the "%Y-%m-%d" format.
            lookback_period (int): Number of days to look back from the end date. Maximum 30 days.
            chunk_size (int): Number of days that each chunk must have.

        Returns:
            Union[Tuple[str]]: Returns two tuples with start and end days divided into several chunks.
        """
        date_format = "%Y-%m-%d"
        end_date = datetime.strptime(end_date, date_format)
        start_dates = []
        end_dates = []

        # Calculate the initial start date for the 30-day lookback period
        initial_start_date = end_date - timedelta(days = lookback_period - 1)

        while lookback_period > 0:
            # Calculate the start date by subtracting the chunk size from the end date
            start_date = end_date - timedelta(days=chunk_size - 1)  # Adjust chunk_size
            start_dates.append(start_date.strftime(date_format))
            end_dates.append(end_date.strftime(date_format))
            end_date = start_date - timedelta(days=1)  # Set end_date to the day before the start date
            lookback_period -= chunk_size

        # Reverse the lists to have them in ascending order
        start_dates.reverse()
        end_dates.reverse()

        # Replace the initial start date with the correct start date
        start_dates[0] = initial_start_date.strftime(date_format)

        return start_dates, end_dates
