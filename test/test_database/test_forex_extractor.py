import unittest
import pandas as pd
from unittest.mock import patch
from pandas.testing import assert_frame_equal
from src.data_extractor.forex_extractor import ForexExtractor

class TestCryptoExtractor(unittest.TestCase):

    input_EURUSD_daily = \
    {
        "Time Series FX (Daily)": {
        "2023-11-14": {
            "1. open": "1.07009",
            "2. high": "1.08228",
            "3. low": "1.06927",
            "4. close": "1.08182"
            },
        "2023-11-13": {
            "1. open": "1.06826",
            "2. high": "1.07061",
            "3. low": "1.06647",
            "4. close": "1.06987"
            },
        "2023-11-10": {
            "1. open": "1.06671",
            "2. high": "1.06930",
            "3. low": "1.06559",
            "4. close": ""
            },
        }
    }

    input_NOKCHF_5mins = \
    {
        "Time Series FX (5min)": {
        "2023-11-14 14:35:00": {
            "1. open": "1.08135",
            "2. high": "1.08201",
            "3. low": "1.08132",
            "4. close": "1.08182"
            },
        "2023-11-14 14:30:00": {
            "1. open": "1.08176",
            "2. high": "1.08187",
            "3. low": "1.08089",
            "4. close": "1.08139"
            },
        }
    }

    expected_EURUSD_daily = pd.DataFrame(data={"open": [1.06826, 1.06671], 
                                                "high": [1.07061, 1.06930],
                                                "low": [1.06647, 1.06559],
                                                "close": [1.06987, 1.06987],
                                                 "symbol_pair": ["EUR/USD", "EUR/USD"],},
                                                index=[pd.to_datetime("2023-11-13"), pd.to_datetime("2023-11-10")],
                                                )

    expected_NOKCHF_5mins = pd.DataFrame(data={"open": [1.08135, 1.08176], 
                                                "high": [1.08201, 1.08187],
                                                "low": [1.08132, 1.08089],
                                                "close": [1.08182, 1.08139],
                                                 "symbol_pair": ["NOK/CHF", "NOK/CHF"],},
                                                index=[pd.to_datetime("2023-11-14 14:35:00"), 
                                                       pd.to_datetime("2023-11-14 14:30:00")],
                                                )

    @patch("src.data_extractor.forex_extractor.ForexExtractor._ForexExtractor__return_request")
    def test_daily_extraction(self, mocked_response):
        mocked_response.return_value = self.input_EURUSD_daily
        EURUSD_extr = ForexExtractor(symbol_pair="EUR/USD")
        output = EURUSD_extr.get_data(period="daily", from_date='2023-11-10', until_date='2023-11-13')
        assert_frame_equal(output, self.expected_EURUSD_daily)

    @patch("src.data_extractor.forex_extractor.ForexExtractor._ForexExtractor__return_request")
    def test_minute_extraction(self, mocked_response):
        mocked_response.return_value = self.input_NOKCHF_5mins
        NOKCHF_extr = ForexExtractor(symbol_pair="NOK/CHF")
        output = NOKCHF_extr.get_data(period="5min", from_date='2023-11-14', until_date='2023-11-14')
        assert_frame_equal(output, self.expected_NOKCHF_5mins)

if __name__ == "__main__":
    unittest.main()
