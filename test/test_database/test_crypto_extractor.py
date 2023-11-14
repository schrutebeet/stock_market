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
                "1a. open (CHF)": "33441.48193380",
                "1b. open (USD)": "37064.13000000",
                "2a. high (CHF)": "33760.75565740",
                "2b. high (USD)": "37417.99000000",
                "3a. low (CHF)": "32781.81258000",
                "3b. low (USD)": "36333.00000000",
                "4a. close (CHF)": "32899.04322180",
                "4b. close (USD)": "36462.93000000",
                "5. volume": "32798.18252000",
                "6. market cap (USD)": "32798.18252000"
            },
            "2023-11-09": 
            {
                "1a. open (CHF)": "32899.04322180",
                "1b. open (USD)": "36462.93000000",
                "2a. high (CHF)": "33112.94200000",
                "2b. high (USD)": "36700.00000000",
                "3a. low (CHF)": "32652.94278420",
                "3b. low (USD)": "36190.17000000",
                "4a. close (CHF)": "33051.25448380",
                "4b. close (USD)": "36631.63000000",
                "5. volume": "6614.68037000",
                "6. market cap (USD)": "6614.68037000"
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
    expected_bitcoin_daily = pd.DataFrame(data={"open_CHF": [33441.48193380], 
                                                "open_USD": [37064.13000000], 
                                                "high_CHF": [33760.75565740],
                                                "high_USD": [37417.99000000],
                                                "low_CHF": [32781.81258000],
                                                "low_USD": [36333.00000000],
                                                "close_CHF": [32899.04322180],
                                                "close_USD": [36462.93000000],
                                                "volume": [32798.18252000],
                                                "market_cap_USD": [32798.18252000],
                                                 "symbol": ["BTC"],},
                                                index=[pd.to_datetime("2023-11-10")],
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
        mocked_response.return_value = self.input_bitcoin_daily
        bitcoin_extr = CryptoExtractor(symbol="BTC", currency="CHF")
        output = bitcoin_extr.get_data(period="daily", from_date='2023-11-10', until_date='2023-11-10')
        assert_frame_equal(output, self.expected_bitcoin_daily)

    @patch("src.data_extractor.crypto_extractor.CryptoExtractor._CryptoExtractor__return_request")
    def test_minute_extraction(self, mocked_response):
        mocked_response.return_value = self.input_ethereum_5mins
        ethereum_extr = CryptoExtractor(symbol="ETH", currency="EUR")
        output = ethereum_extr.get_data(period="5min", from_date='2023-11-09', until_date='2023-11-09')
        assert_frame_equal(output, self.expected_ethereum_5mins)

if __name__ == "__main__":
    unittest.main()
