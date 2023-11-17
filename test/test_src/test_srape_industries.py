import unittest
import datetime
from freezegun import freeze_time
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest.mock import patch
from src.scrape_industries import IndustriesScraper

class TestIndustriesScraper(unittest.TestCase):

    html = '''
            <html>
            <body>
                <table>
                <tbody>
                    <tr>
                    <td>Symbol1</td>
                    <td>Company1</td>
                    <td>Industry1</td>
                    <td>MarketCap1</td>
                    </tr>
                </tbody>
                </table>
            </body>
            </html>
    '''

    expected_extraction = pd.DataFrame(
        {
            "symbol": ["Symbol1"],
            "company": ["Company1"],
            "industry": ["Industry1"],
            "marketcap": ["MarketCap1"],
            "timestamp": [pd.to_datetime("2023-11-17")],
        }
    )

    csv = "symbol,name,exchange,assetType,ipoDate,delistingDate,status\n"\
          "A,Agilent Technologies Inc,NYSE,Stock,1999-11-18,null,Active\n"\
          "AA,Alcoa Corp,NYSE,Stock,2016-10-18,null,Active\n"\
          "AAA,AXS First Priority CLO Bond ETF,NYSE ARCA,ETF,2020-09-09,null,Active\n"\
          "AAAU,Goldman Sachs Physical Gold ETF,BATS,ETF,2018-08-15,null,Active\n"

    def setUp(self):
        mock_url = "https://www.my_mock_webpage.com"
        self.industry_instance = IndustriesScraper(mock_url)

    @freeze_time("2023-11-17")
    @patch("selenium.webdriver.Chrome")
    def test_extraction(self, mocked_driver):
        driver = mocked_driver.return_value
        driver.page_source = self.html
        self.industry_instance.extraction()
        output = self.industry_instance.web_data
        assert_frame_equal(output, self.expected_extraction)

    @patch("requests.Session.get")
    def test_alpha_stocks(self, mocked_requests):
        s = mocked_requests.return_value
        s.content.decode.return_value = self.csv
        self.industry_instance.alpha_stocks()

if __name__ == "__main__":
    unittest.main()
