import unittest
from pathlib import Path
import json
import pandas as pd
from unittest.mock import patch
from pandas.testing import assert_frame_equal
from src.data_extractor.crypto_extractor import CryptoExtractor

class TestCryptoExtractor(unittest.TestCase):

    endpoint_bitcoin_daily = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol="\
                             "BTC&market=CNY&apikey=mock_key"
    endpoint_ethereum_5mins = "https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=ETH&market=EUR&"\
                              "interval=5min}&outputsize=full&apikey=mock_key"
    input_bitcoin_daily = \
    {
        "Time Series (Digital Currency Daily)": {
            "2023-11-10": 
            {
                "1a. open (USD)": "35399.13000000",
                "1b. open (USD)": "35399.13000000",
                "2a. high (USD)": "35419.29000000",
                "2b. high (USD)": "35419.29000000",
                "3a. low (USD)": "35250.00000000",
                "3b. low (USD)": "35250.00000000",
                "4a. close (USD)": "35419.29000000",
                "4b. close (USD)": "35419.29000000",
                "5. volume": "1520.60543000",
                "6. market cap (USD)": "1520.60543000"
            },
            "2023-11-09": 
            {
                "1a. open (USD)": "35046.09000000",
                "1b. open (USD)": "35046.09000000",
                "2a. high (USD)": "35888.00000000",
                "2b. high (USD)": "35888.00000000",
                "3a. low (USD)": "34523.06000000",
                "3b. low (USD)": "34523.06000000",
                "4a. close (USD)": "35399.12000000",
                "4b. close (USD)": "35399.12000000",
                "5. volume": "38688.73692000",
                "6. market cap (USD)": "38688.73692000"
            },
        }
    }
    input_ethereum_5mins = \
    {
        "Time Series Crypto (5min)": {
            "2023-11-09 22:40:00": {
                "1. open": "1889.90000",
                "2. high": "1890.50000",
                "3. low": "1889.90000",
                "4. close": "1890.49000",
                "5. volume": 1234
            },
            "2023-11-08 22:35:00": {
                "1. open": "1890.49000",
                "2. high": "1890.50000",
                "3. low": "1888.27000",
                "4. close": "1889.90000",
                "5. volume": 1041
            },
        }
    }
    expected_bitcoin_daily = pd.DataFrame(data={"open_BTC": [35046.09000000], 
                                                "open_USD": [35046.09000000], 
                                                "high_BTC": [1890.50000],
                                                "high_USD": [1890.50000],
                                                "low_BTC": [1889.90000],
                                                "low_USD": [1889.90000],
                                                "close_BTC": [1890.49000],
                                                "close_USD": [1890.49000],
                                                "volume_BTC": [1234],
                                                "volume_USD": [1234]},
                                                index=[pd.to_datetime("2023-11-09 22:40:00")],
                                                )
    expected_ethereum_5mins = pd.DataFrame(data={"open": [1889.90000], 
                                                 "high": [1890.50000],
                                                 "low": [1889.90000],
                                                 "close": [1890.49000],
                                                 "volume": [1234],
                                                 "currency": ["EUR"],
                                                 "symbol": ["ETH"],},
                                                 index=[pd.to_datetime("2023-11-09 22:40:00")],
                                                )
    
    @patch("src.data_extractor.crypto_extractor.CryptoExtractor._CryptoExtractor__return_request")
    def test_daily_extraction(self, mocked_response):
        mocked_response.return_value = self.input_ethereum_5mins
        ethereum_extr = CryptoExtractor(symbol="ETH", currency="EUR")
        output = ethereum_extr.get_data(period="5min", from_date='2023-11-09', until_date='2023-11-09')
        assert_frame_equal(output, self.expected_ethereum_5mins)

if __name__ == "__main__":
    unittest.main()
