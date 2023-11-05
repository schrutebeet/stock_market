"""
PACKAGES
"""
import csv
import datetime
import io
import logging
import random
import sys
import time
from urllib.request import Request, urlopen
from pathlib import Path

import pandas as pd
import requests
import selenium
from bs4 import BeautifulSoup
from config.config import Config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import utils.log_config as log_config
from webdriver_manager.chrome import ChromeDriverManager

import utils.error_handling as errors
from dependencies.authenticator import api_key

"""
VARIABLES
"""


class IndustriesScraper:
    def __init__(self, url_to_webpage) -> None:
        self.url = url_to_webpage
        self.raw_data = pd.DataFrame()
        self.web_data = pd.DataFrame()
        self.alpha_data = pd.DataFrame()
        self.joint_table = pd.DataFrame()

    def run_scraper(self) -> pd.DataFrame:
        self.extraction()
        self.alpha_stocks()
        self.table_unions()
        return self.joint_table

    def extraction(self) -> None:
        info = {"symbol": [], "company": [], "industry": [], "market_cap": []}
        chromedriver_path = str(Path(Config.chromedriver_path))
        chrome_options = webdriver.ChromeOptions()
        try:
            chrome_options.binary_location = chromedriver_path
        except:
            logging.error("Incorrect ChromeDriver path. Check on the config file.")
        chrome_options.add_argument("--headless")
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except selenium.common.exceptions.WebDriverException as e:
            logging.error(
                f"Web scraper could not be carried out because "
                "there is no internet connection or there is no driver installed."
            )
            raise errors.InternetError()
        driver.set_window_size(1366, 768)
        driver.get(self.url)
        try:
            # Consent cookies
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.fc-button.fc-cta-consent.fc-primary-button")
                )
            ).click()
        except Exception as e:
            logging.info("Cookies banner was not found")
            print(f"{e}")
        try:
            # Dismiss newsletter banner
            WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[class*='Close'], [class*='close']"))
            ).click()
            # in case the close driver does not work
            element = driver.switch_to.active_element
            element.send_keys(Keys.ESCAPE)
        except Exception as e:
            logging.info("Newsletter banner was not found")
            print(f"{e}")

        # Proceed with scraping
        num_pages = 0
        while True:
            try:
                html = driver.page_source
                soup = BeautifulSoup(html, "lxml")
                table = soup.find("tbody")
                rows = table.find_all("tr")
                for tr in rows:
                    td = tr.find_all("td")
                    row = [tr.text for tr in td]
                    info["symbol"].append(row[0])
                    info["company"].append(row[1])
                    info["industry"].append(row[2])
                    info["market_cap"].append(row[3])
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'Next')]")
                    )
                ).click()
                time.sleep(random.choice([2, 3]))
                num_pages += 1
            except selenium.common.exceptions.TimeoutException as e:
                if num_pages > 0:
                    logging.info(
                        f"Successfully web-scraped {num_pages} pages and saved {len(info['symbol'])} symbols."
                    )
                    log_config.add_separator()
                    break
                else:
                    logging.error(
                        f"Scraped zero pages. Check on the selenium code and update if necessary."
                    )
                    return None
        self.web_data = pd.DataFrame(info)
        driver.quit()

    def alpha_stocks(self, day=datetime.date.today()) -> None:
        CSV_URL = f"https://www.alphavantage.co/query?function=LISTING_STATUS&date={day}&state=active&apikey={api_key}"
        with requests.Session() as s:
            download = s.get(CSV_URL)
            decoded_content = download.content.decode("utf-8")
            cr = csv.reader(decoded_content.splitlines(), delimiter=",")
            csv_memory = io.StringIO()
            to_csv = csv.writer(csv_memory, delimiter=",")
            for row in cr:
                to_csv.writerow(row)
            csv_memory.seek(0)
            df = pd.read_csv(csv_memory)
            df.columns = [
                "symbol",
                "name",
                "exchange",
                "assetType",
                "ipoDate",
                "delistingDate",
                "status",
            ]
            df = df[df["assetType"] == "Stock"]
            self.alpha_data = df

    def table_unions(self):
        stockanalysis = self.web_data
        alpha = self.alpha_data
        df_merge = pd.merge(
            stockanalysis, alpha, on="symbol", how="outer"
        ).drop_duplicates()
        df_merge["company_name"] = df_merge.name.combine_first(
            df_merge.company
        )  # Coalesce
        df_merge = df_merge[
            [
                "symbol",
                "company_name",
                "exchange",
                "status",
                "ipoDate",
                "industry",
                "market_cap",
            ]
        ]
        self.joint_table = df_merge


"""
EXECUTION
"""
if __name__ == "__main__":
    table = IndustriesScraper("https://stockanalysis.com/stocks/").run_scraper()
    print(table)
