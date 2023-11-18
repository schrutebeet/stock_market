import logging
import sys
import time

import utils.log_config as log_config
from src.models import Model
from src.scrape_industries import IndustriesScraper
from src.stock import Stock
from utils.util_funcs import timeit

class Runner:
    @timeit
    def run(fetch_type="fetch_daily", train_size=0.8, rolling_window=60, scale=True):
        log_config.add_separator()
        logging.info(f"Initializing web scraper")
        ind_scraper = IndustriesScraper("https://stockanalysis.com/stocks/")
        scraped_tb = ind_scraper.run_scraper()
        for symbol in scraped_tb.symbol[:]:
            try:
                stock = Stock(symbol)
                getattr(stock, fetch_type)()
                stock.prepare_train_test_sets(train_size, rolling_window, scale=scale)
                base_for_model = Model(stock)
                accuracy = base_for_model.lstm_nn(viz=False)
                logging.info(f"Successfully run framework for symbol {symbol}. Score: {accuracy*100:.2f}%")
            except Exception as e:
                logging.error(f"Process aborted for symbol {symbol}")
                log_config.add_separator()
        logging.info("SUCCESS: END OF PROCESS")


def main():
    Runner.run()


if __name__ == "__main__":
    main()
