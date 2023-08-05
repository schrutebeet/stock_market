"""
OBJECTIVE OF THIS MODULE
------------------------
Define funtions for fetching data from AlphaVantage API
"""
import logging
import pandas as pd
import requests
import numpy as np
from dependencies.authenticator import api_key
from sklearn.preprocessing import MinMaxScaler
import utils.error_handling as errors

class Stock:
    
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol
        self.api_key = api_key
        self.data = pd.DataFrame()

    def fetch_intraday(self, start_date=None, end_date=None) -> pd.DataFrame:
        """
        Fetch intraday data for a particular stock instance.

        Args:
            start_date (str): An initial date string of the format 'DDD-MM-YYYY'.
                              If no value is given, it assumes no minimum date.
            end_date (str): A final date string of the format 'DDD-MM-YYYY'
                            If no value is given, it assumes no maximum date.

        Returns:
            pd.DataFrame: a Dataframe containing intraday prices for a particular stock
        """
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY'\
              f'&symbol={self.stock_symbol}&outputsize=full&interval=1min&apikey={self.api_key}'
        r = requests.get(url)
        json_data = r.json()['Time Series (1min)']
        df = pd.DataFrame(json_data).T.sort_index()
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric, errors='coerce')

        if start_date is not None:
            start_date = pd.to_datetime(f'{start_date} 00:00:00')
            df = df[df.index >= start_date]
        if end_date is not None:
            end_date = pd.to_datetime(f'{end_date} 23:59:59')
            df = df[df.index <= end_date]

        df.columns = ['open', 'high', 'low', 'close', 'volume']
        if df.empty:
            logging.error('AlphaVantage: returns an empty Dataframe.')
            raise errors.EmptyDataframeError()

    def fetch_daily(self, start_date=None, end_date=None) -> None:
        """
        Fetch daily data for a particular stock instance.

        Args:
            start_date (str): An initial date string of the format 'DDD-MM-YYYY'.
                              If no value is given, it assumes no minimum date.
            end_date (str): A final date string of the format 'DDD-MM-YYYY'
                            If no value is given, it assumes no maximum date.

        Returns:
            pd.DataFrame: a Dataframe containing daily prices for a particular stock
        """
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'\
              f'&symbol={self.stock_symbol}&outputsize=full&apikey={self.api_key}'
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            logging.error('AlphaVantage: Could not connect to the internet')
            raise e
        try:
            json_data = r.json()['Time Series (Daily)']
        except KeyError as e:
            logging.error('AlphaVantage: JSON does not have a "Time Series (Daily)" key.')
            raise e
        df = pd.DataFrame(json_data).T.sort_index()
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric, errors='coerce')
        if start_date is not None:
            start_date = pd.to_datetime(start_date)
            df = df[df.index >= start_date]
        if end_date is not None:
            end_date = pd.to_datetime(end_date)
            df = df[df.index <= end_date]
        df.columns = ['open', 'high', 'low', 'non_adj_close', 'close', 'volume', 'dividend_amount', 'split_coeff']
        if df.empty:
                logging.error('AlphaVantage: returns an empty Dataframe.')
                raise errors.EmptyDataframeError(self.stock_symbol)
        self.data = df
        
    def _treat_missing_data(self) -> pd.DataFrame:
        """
        If a value is missing, fill it with the previous value

        Args:
            df (pd.DataFrame): Dataframe containing raw information on a particular stock.

        Returns:
            df (pd.DataFrame): Dataframe containing non-missing information on a particular stock.
        """
        df = self.data.fillna(method='ffill')
        return df
    
    def prepare_train_test_sets(self, train_size, rolling_window, scale) -> None:
        """
        Once we have the core information on a stock, we can proceed to prepare the data for modelling purposes.

        Args:
            df (pd.DataFrame): Dataframe containing raw information on a particular stock.
            train_size (float): Value between 0 and 1. Percentage of the whole df dedicated to the train set.
            rolling_window (int): Set of days from which the model will feed to give an output.

        Returns:
            tuple: A tuple containing the following objects:
            - x_train (np.array): Set of past prices for training purposes during training.
            - y_train (np.array): Target to be predicted by the x_train set.
            - x_test (np.array): Set of past prices for testing purposes.
            - y_test (np.array): Target to be predicted by the x_test set during testing.
        """
        self.train_size = train_size
        self.rolling_window = rolling_window
        if not 0 < train_size < 1:
            logging.error("Argument 'train_size' must be a value between 0 and 1.")
            raise ValueError()
        if not rolling_window > 0:
            logging.error("Argument 'train_size' must be higher than 0.")
            raise ValueError()
        df = self._treat_missing_data()
        close_prices = df['close'].to_numpy()
        # We start with the train set
        training_data_len = int(round(len(close_prices)* train_size, 0))
        if training_data_len < rolling_window:
            logging.error('Preprocess: training data size cannot be smaller than rolling window size.')
            raise errors.TrainingLengthError(training_data_len, rolling_window)
        train_data = close_prices[0: training_data_len].reshape(-1,1)
        if scale:
            scaler = MinMaxScaler()
            train_data = scaler.fit_transform(train_data)
        x_train = np.empty((0, rolling_window))
        y_train = train_data[rolling_window: , 0]
        for i in range(rolling_window, len(train_data)):
            x_train = np.vstack((x_train, train_data[i-rolling_window:i, 0]))
        # Adding a third dimension as a requirement from TensorFlow 
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        # Now, let's proceed with the test set
        # We subtract 60 because to output the first prediction on test 
        # we need data on the 60 last close prices
        test_data = close_prices[training_data_len-rolling_window: ].reshape(-1,1)
        if scale:
            test_data = scaler.transform(test_data)
            self.scaler = scaler
        else:
            self.scaler = scale
        x_test = np.empty((0, rolling_window))
        y_test = test_data[rolling_window: , 0]
        for i in range(rolling_window, len(test_data)):
            x_test = np.vstack((x_test, test_data[i-rolling_window: i, 0]))
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1)) 
        
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test
