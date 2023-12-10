import unittest
import pandas as pd
from unittest.mock import patch
from pandas.testing import assert_frame_equal
from freezegun import freeze_time
from src.data_extractor.stock_extractor import StockExtractor

class TestCryptoExtractor(unittest.TestCase):

    input_TSLA_daily_1 = \
    {
        "Time Series (Daily)": {
            "2023-11-01":
            {
                "1. open": "0.812356",
                "2. high": "0.884853",
                "3. low": "0.790474",
                "4. close": "0.850372",
                "5. adjusted close": "0.850372",
                "6. volume": "34567",
                "7. dividend amount": "0",
                "8. split coefficient": "1.0",
            },
        }
    }

    input_TSLA_daily_2 = \
    {
        "Time Series (Daily)": {
            "2023-10-31":
            {
                "1. open": "0.802356",
                "2. high": "0.874853",
                "3. low": "",
                "4. close": "0.840372",
                "5. adjusted close": "0.840372",
                "6. volume": "34534",
                "7. dividend amount": "0.8",
                "8. split coefficient": "1.0",
            },
        }
    }

    input_TSLA_daily = [input_TSLA_daily_1, input_TSLA_daily_2]

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
                                                "split_coeff": [1.0, 1.0],
                                                "datetime": [pd.to_datetime("2023-11-01"), pd.to_datetime("2023-10-31")],
                                                "timestamp": [pd.to_datetime("2023-11-17 00:00:00"), pd.to_datetime("2023-11-17 00:00:00")],
                                                "symbol": ["TSLA", "TSLA"],},
                                                index=[pd.to_datetime("2023-11-01"), pd.to_datetime("2023-10-31")],
                                                )

    expected_AAPL_5mins = pd.DataFrame(data={"open": [18.89900], 
                                                 "high": [18.90500],
                                                 "low": [18.89900],
                                                 "close": [18.90490],
                                                 "volume": [1234],
                                                 "datetime": [pd.to_datetime("2023-11-09 22:40:00")],
                                                 "timestamp": [pd.to_datetime("2023-11-17 00:00:00")],
                                                 "symbol": ["AAPL"],},
                                                 index=[pd.to_datetime("2023-11-09 22:40:00")],
                                                )

    @freeze_time("2023-11-17 00:00:00")
    @patch("src.data_extractor.stock_extractor.StockExtractor._StockExtractor__return_request")
    def test_daily_extraction(self, mocked_response):
        mocked_response.side_effect = self.input_TSLA_daily
        tsla_extr = StockExtractor(symbol="TSLA")
        output = tsla_extr.get_data(period="daily", from_date='2023-10-31', until_date='2023-11-01')
        assert_frame_equal(output, self.expected_TSLA_daily)

    @freeze_time("2023-11-17 00:00:00")
    @patch("src.data_extractor.stock_extractor.StockExtractor._StockExtractor__return_request")
    def test_minute_extraction(self, mocked_response):
        mocked_response.return_value = self.input_AAPL_5mins
        aapl_extr = StockExtractor(symbol="AAPL")
        output = aapl_extr.get_data(period="5min", from_date='2023-11-09', until_date='2023-11-09')
        assert_frame_equal(output, self.expected_AAPL_5mins)

if __name__ == "__main__":
    unittest.main()
