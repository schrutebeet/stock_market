"""
PACKAGES
"""
import csv
import datetime
import io
import logging
import random
import time
from typing import List, Union
from pathlib import Path

import pandas as pd
import math
import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import utils.error_handling as errors
import utils.log_config as log_config
from config.config import Config
from dependencies.authenticator import api_key
from database.connection import engine
from database.utils_db import UtilsDB
from database.connection import SessionLocal

"""
VARIABLES
"""


class IndustriesScraper:
    def __init__(self, url_to_webpage) -> None:
        self.url = url_to_webpage
        self.web_data = pd.DataFrame()
        self.alpha_data = pd.DataFrame()
        self.joint_table = pd.DataFrame()
        self.dbsession = SessionLocal()

    def run_scraper(self) -> pd.DataFrame:
        """Run all methods sequentially to get the joint results of all scrapings.

        Returns:
            pd.DataFrame: Dataframe containing information on different assets, as well as 
                          their industry group.
        """
        self.extraction()
        self.alpha_stocks()
        self.table_unions()
        self.insert_tables_in_db(50_000)
        return self.joint_table

    def extraction(self) -> None:
        """Scrape information on industry and market capitalization for the vast majority of US stocks.

        Raises:
            errors.InternetError: Raise error if no internet connection is found.
        """
        info = {"symbol": [], "company": [], "industry": [], "marketcap": []}
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
                    (
                        By.CSS_SELECTOR,
                        "button.fc-button.fc-cta-consent.fc-primary-button",
                    )
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
                    info["marketcap"].append(row[3])
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
                ).click()
                time.sleep(random.choice([2, 3]))
                num_pages += 1
            except selenium.common.exceptions.TimeoutException as e:
                if num_pages > 0:
                    logging.info(f"Successfully web-scraped {num_pages} pages and saved {len(info['symbol'])} symbols.")
                    log_config.add_separator()
                    break
                else:
                    logging.error(f"Scraped zero pages. Check on the selenium code and update if necessary.")
                    return None
        web_data = pd.DataFrame(info)
        web_data['timestamp'] = datetime.datetime.utcnow()
        self.web_data = web_data
        driver.quit()

    def alpha_stocks(self, day: datetime.datetime=datetime.date.today()) -> None:
        """Get stocks' general information from the AlphaVantage API.

        Args:
            day (datetime.datetime, optional): Set the day for information on that specific time. 
                                               Defaults to datetime.date.today().
        """
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
                "assettype",
                "ipodate",
                "delistingdate",
                "status",
            ]
            df['delistingdate'] = pd.to_datetime(df['delistingdate']).fillna(datetime.datetime.strptime('31-12-9999', '%d-%m-%Y'))
            df['ipodate'] = pd.to_datetime(df['ipodate']).fillna(datetime.datetime.strptime('31-12-9999', '%d-%m-%Y'))
            df['timestamp'] = datetime.datetime.utcnow()
            self.alpha_data = df

    def table_unions(self):
        """Unite tables from both data sources.
        """
        stockanalysis = self.web_data
        alpha = self.alpha_data[self.alpha_data['assettype'] == "Stock"].copy()
        df_merge = pd.merge(stockanalysis, alpha, on="symbol", how="outer").drop_duplicates().reset_index(drop=True)
        df_merge["companyname"] = df_merge.name.combine_first(df_merge.company)  # Coalesce
        df_merge = df_merge[
            [
                "symbol",
                "companyname",
                "exchange",
                "status",
                "ipodate",
                "industry",
                "marketcap",
            ]
        ]
        df_merge['ipodate'] = pd.to_datetime(df_merge['ipodate']).fillna(datetime.datetime.strptime('31-12-9999', '%d-%m-%Y'))
        df_merge['timestamp'] = datetime.datetime.utcnow()
        self.joint_table = df_merge

    def insert_tables_in_db(self, batch_size: int = 100_000) -> None:
        """Insert values of each extracted table in the DB."""
        info_wrapper = [(self.web_data, "stock_industries"), 
                        (self.alpha_data, "stock_info"), 
                        (self.joint_table, "stock_merged")]
        # Connect to database
        #conn = self.engine.connect()
        utils = UtilsDB()
        # Check whether any new tables should be created
        utils.create_new_models()
        for tuple_ in info_wrapper:
            len_df = len(tuple_[0])
            model = utils.get_class_with_table_name(tuple_[1])
            if len_df > batch_size:
                output_df = self._divide_df_in_batches(tuple_[0], batch_size)
            else:
                output_df = [tuple_[0]]
            for df in output_df:
                # argument "orient='records'" especifies the dictionary should be made row-wise
                dictionary_rows = df.to_dict(orient='records')
                self.dbsession.bulk_insert_mappings(model, dictionary_rows)
            # Commit the changes to the database for each model
            self.dbsession.commit()
        # Close connection
        self.dbsession.close()

    @staticmethod
    def _divide_df_in_batches(input_df: pd.DataFrame, batch_size: int) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        """Divide dataframe in smaller pieces for speed improvement.
        """
        n_chunks = math.ceil(len(input_df) / batch_size)
        output_df = []
        starting_row, ending_row = 0, batch_size
        for n in range(n_chunks):
            chunked_df = input_df.iloc[starting_row : ending_row, ]
            output_df.append(chunked_df)
            starting_row += batch_size
            ending_row += batch_size
        return output_df

"""
EXECUTION
"""
if __name__ == "__main__":
    table = IndustriesScraper("https://stockanalysis.com/stocks/").run_scraper()
