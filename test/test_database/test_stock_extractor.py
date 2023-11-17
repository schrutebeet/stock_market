import unittest
import pandas as pd
from unittest.mock import patch
from pandas.testing import assert_frame_equal
from src.data_extractor.stock_extractor import StockExtractor

class TestCryptoExtractor(unittest.TestCase):

    input_TSLA_daily = \
    {
        "Time Series (Daily)": {
            "2023-11-01":
            {
                "TODO1": "0.812356",
                "TODO2": "0.884853",
                "TODO3": "0.790474",
                "TODO4": "0.850372",
                "TODO5": "0.850372",
                "TODO6": "34567",
                "TODO7": "0",
                "TODO8": "1",
            },
            "2023-10-31":
            {
                "TODO1": "0.802356",
                "TODO2": "0.874853",
                "TODO3": "",
                "TODO4": "0.840372",
                "TODO5": "0.840372",
                "TODO6": "34534",
                "TODO7": "0.8",
                "TODO8": "1",
            },
        }
    }

    input_AAPL_5mins = \
    {
        "Time Series (5min)": {
            "2023-11-09 22:40:00": {
                "1. open": "18.89900",
                "2. high": "18.90500",
                "3. low": "18.89900",
                "4. close": "18.90490",
                "5. volume": 1234
            },
            "2023-11-08 22:35:00": {
                "1. open": "",
                "2. high": "18.90500",
                "3. low": "18.88270",
                "4. close": "18.89900",
                "5. volume": 1041
            },
        }
    }

    expected_TSLA_daily = pd.DataFrame(data={"open": [0.812356, 0.802356], 
                                                "high": [0.884853, 0.874853], 
                                                "low": [0.790474, 0.790474],
                                                "close": [0.850372, 0.840372],
                                                "adj_close": [0.850372, 0.840372],
                                                "volume": [34567, 34534],
                                                "dividend_amount": [0, 0.8],
                                                "split_coeff": [1, 1],
                                                "symbol": ["TSLA", "TSLA"],},
                                                index=[pd.to_datetime("2023-11-01"), pd.to_datetime("2023-10-31")],
                                                )

    expected_AAPL_5mins = pd.DataFrame(data={"open": [18.89900, 18.89900], 
                                                 "high": [18.90500, 18.90500],
                                                 "low": [18.89900, 18.88270],
                                                 "close": [18.90490, 18.89900],
                                                 "volume": [1234, 1041],
                                                "symbol": ["AAPL", "AAPL"],},
                                                 index=[pd.to_datetime("2023-11-09 22:40:00"),
                                                        pd.to_datetime("2023-11-08 22:35:00")],
                                                )

    @patch("src.data_extractor.stock_extractor.StockExtractor._StockExtractor__return_request")
    def test_daily_extraction(self, mocked_response):
        mocked_response.return_value = self.input_TSLA_daily
        tsla_extr = StockExtractor(symbol="TSLA")
        output = tsla_extr.get_data(period="daily", from_date='2023-10-31', until_date='2023-11-01')
        assert_frame_equal(output, self.expected_TSLA_daily)

    @patch("src.data_extractor.stock_extractor.StockExtractor._StockExtractor__return_request")
    def test_minute_extraction(self, mocked_response):
        mocked_response.return_value = self.input_AAPL_5mins
        aapl_extr = StockExtractor(symbol="AAPL")
        output = aapl_extr.get_data(period="5min", from_date='2023-11-09', until_date='2023-11-09')
        assert_frame_equal(output, self.expected_AAPL_5mins)

if __name__ == "__main__":
    unittest.main()
