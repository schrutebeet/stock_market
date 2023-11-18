import unittest
import datetime
from freezegun import freeze_time
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest.mock import patch
from src.scrape_industries import IndustriesScraper

class TestIndustriesScraper(unittest.TestCase):

    html_expected_extraction = '''
            <html>
            <body>
                <table>
                <tbody>
                    <tr>
                    <td>ABCD</td>
                    <td>ABCDesigns Inc</td>
                    <td>Technology</td>
                    <td>3.8B</td>
                    </tr>
                </tbody>
                </table>
            </body>
            </html>
    '''

    expected_extraction = pd.DataFrame(
        {
            "symbol": ["ABCD"],
            "company": ["ABCDesigns Inc"],
            "industry": ["Technology"],
            "marketcap": ["3.8B"],
            "timestamp": [pd.to_datetime("2023-11-17")],
        }
    )

    csv_alpha_stocks = "symbol,name,exchange,assetType,ipoDate,delistingDate,status\n"\
                       "ABCD,ABCDesigns Inc,NYSE,Stock,1999-11-18,null,Active\n"\
                       "EFGH,EpicForge Technologies,NYSE,Stock,2016-10-18,null,Active\n"\
                       "IJKL,InnoJolt Labs,NYSE ARCA,ETF,2020-09-09,null,Active\n"\
                       "MNOP,MegaNova Organic Products Corp,BATS,ETF,2018-08-15,null,Active\n"

    expected_alpha_stocks = pd.DataFrame(
        {
            "symbol": ["ABCD", "EFGH", "IJKL", "MNOP"],
            "name": ["ABCDesigns Inc", "EpicForge Technologies", "InnoJolt Labs", "MegaNova Organic Products Corp"],
            "exchange": ["NYSE", "NYSE", "NYSE ARCA", "BATS"],
            "assettype": ["Stock", "Stock", "ETF", "ETF"],
            "ipodate": [pd.to_datetime("1999-11-18"), pd.to_datetime("2016-10-18"),
                        pd.to_datetime("2020-09-09"), pd.to_datetime("2018-08-15"),],
            "delistingdate": [datetime.datetime.strptime('31-12-9999', '%d-%m-%Y')] * 4,
            "status": ["Active", "Active", "Active", "Active"],
            "timestamp": [pd.to_datetime("2023-11-17"), pd.to_datetime("2023-11-17"),
                          pd.to_datetime("2023-11-17"), pd.to_datetime("2023-11-17")],
        }
    )

    def setUp(self):
        mock_url = "https://www.my_mock_webpage.com"
        self.industry_instance = IndustriesScraper(mock_url)

    @freeze_time("2023-11-17")
    @patch("selenium.webdriver.Chrome")
    def test_extraction(self, mocked_driver):
        driver = mocked_driver.return_value
        driver.page_source = self.html_expected_extraction
        self.industry_instance.extraction()
        output = self.industry_instance.web_data
        assert_frame_equal(output, self.expected_extraction)

    @freeze_time("2023-11-17")
    @patch("requests.Session.get")
    def test_alpha_stocks(self, mocked_requests):
        s = mocked_requests.return_value
        s.content.decode.return_value = self.csv_alpha_stocks
        self.industry_instance.alpha_stocks()
        output = self.industry_instance.alpha_data
        assert_frame_equal(output, self.expected_alpha_stocks)

if __name__ == "__main__":
    unittest.main()
