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
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd
import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy.sql import text

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
        self.extraction()
        self.alpha_stocks()
        self.table_unions()
        self.insert_tables_in_db()
        return self.joint_table

    def extraction(self) -> None:
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
        stockanalysis = self.web_data
        alpha = self.alpha_data[self.alpha_data['assettype'] == "Stock"].copy()
        df_merge = pd.merge(stockanalysis, alpha, on="symbol", how="outer").drop_duplicates()
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

    def insert_tables_in_db(self):
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
            #print(tuple_[0][~pd.notna(tuple_[0]['timestamp'])])
            model = utils.get_class_with_table_name(tuple_[1])
            """
            values_placeholder = ["%s"] * len(tuple_[0].columns)
            column_names = tuple_[0].columns.tolist()
            insert_query = f"INSERT INTO {tuple_[1]} ({', '.join(column_names)}) VALUES ({', '.join(values_placeholder)})"
            """
            df_in_tuples = tuple_[0].apply(tuple, axis=1)
            data = [dict(zip(tuple_[0].columns, row)) for row in df_in_tuples]

            for row in data:
                new_row_obj = model(**row)
                self.dbsession.add(new_row_obj)
            
            # Commit the changes to the database for each model
            self.dbsession.commit()
        # Close connection
        self.dbsession.close()


"""
EXECUTION
"""
if __name__ == "__main__":
    table = IndustriesScraper("https://stockanalysis.com/stocks/").run_scraper()
