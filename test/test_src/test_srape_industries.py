import unittest
from unittest.mock import patch
from src.scrape_industries import IndustriesScraper

class TestIndustriesScraper(unittest.TestCase):

    def setUp(self):
        mock_url = "https://www.my_mock_webpage.com"
        industry_instance = IndustriesScraper(mock_url)
        self.industry_instance = industry_instance

    @patch("webdriver.ChromeOptions")
    def test_extraction(self, mocked_driver):
        self.industry_instance.extraction()
        pass

    @patch("requests.Session")
    def test_alpha_stocks(self, mocked_requests):
        mocked_requests.return_value = 
        self.industry_instance.alpha_stocks()

