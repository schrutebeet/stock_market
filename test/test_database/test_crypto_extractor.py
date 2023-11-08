import unittest
import requests
from unittest.mock import patch
from src.data_extractor.crypto_extractor import CryptoExtractor

class TestCryptoExtractor(unittest.TestCase):

    expected_bitcoin_daily = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol="\
                             "BTC&market=CNY&apikey=mock_key"
    expected_ethereum_5mins = "https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol=ETH&market=EUR&"\
                              "interval=5min}&outputsize=full&apikey=mock_key"
    
    mock_bitcoin_json = {"Time Series (Digital Currency Daily)": {
                                                                  "date": "2023-11-08",
                                                                  "1. open": 50,
                                                                  "2. high": 60,
                                                                  "3. low": 40,
                                                                  "4. close": 55,
                                                                  "5. volume": 350,
                                                                  }}

    mock_ethereum_json = {"Time Series (Digital Currency Daily)": {
                                                                   "date": "2023-11-08",
                                                                   "1a. open (EUR)": 10,
                                                                   "1b. open (USD)": 4,
                                                                   "2a. high (EUR)": 12,
                                                                   "2b. high (USD)": 5,
                                                                   "3a. low (EUR)": 6,
                                                                   "3b. low (USD)": 2,
                                                                   "4a. close (EUR)": 8,
                                                                   "4b. close (USD)": 3,
                                                                   "5. volume": 100,
                                                                   "6. market cap (USD)": 150_000,
                                                                  }}

    @patch("requests.get")
    def test_daily_extraction(self, mocked_response):
        mocked_response.return_value = self.mock_ethereum_json
        ethereum_extr = CryptoExtractor(symbol="ETH", api_key="mock_key", currency="EUR")
        output = ethereum_extr.get_data(period="daily", from_date='2023-11-08', until_date='2023-11-09')
        print(output)

if __name__ == "__main__":
    unittest.runner()
