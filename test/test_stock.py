import unittest
import pandas as pd
from src.stock import Stock
from unittest.mock import MagicMock, patch


class TestStock(unittest.TestCase):

    test_dict = {"2023-08-04 19:55:00": {
                                    "1. open": "144.2400",
                                    "2. high": "144.2400",
                                    "3. low": "144.2400",
                                    "4. close": "144.2400",
                                    "5. volume": "5"
                                    },
            "2023-08-04 19:54:00": {
                                    "1. open": "144.0500",
                                    "2. high": "144.0500",
                                    "3. low": "144.0500",
                                    "4. close": "144.0500",
                                    "5. volume": "6"
                                    }}
    
    # this will allow us to use a mock of the requests.get method 
    @patch('requests.get')
    # the argument 'mock_get' is the method mocked by the decorator
    def test_fetch_intraday_successful(self, mock_get):
        # Creating an instance of a mock function from unittest
        mock_response = MagicMock()
        # define the response to give
        mock_response.json.return_value = self.test_dict
        # define the response to the request.get method
        mock_get.return_value = mock_response  
        # modify that response using the transform method from the Stock Class
        mock_get.return_value = Stock.transform_json_to_df(mock_get.return_value, None, None)
        self.assertEqual(mock_get.return_value.columns.tolist(), ['open', 'high', 'low', 'close', 'volume'])

if __name__ == "__main__":
    TestStock().test_fetch_intraday_successful()
    unittest.main()
