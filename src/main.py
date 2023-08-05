import sys
import time
import logging
from utils import log_config
from stock import Stock
from src.models import Model
from scrape_industries import IndustriesScraper

def timeit(func):
    @staticmethod
    def wrapper(*args, **kwargs):
        start = time.time()
        # runs the function
        function = func(*args, **kwargs)
        end = time.time()
        print("\n","-"*30, sep="")
        print(f'Elapsed time: {(end - start):.2f} seconds')
        print("-"*30, "\n")
        return function
    return wrapper

class Runner():
    @timeit
    def run(fetch_type='fetch_daily', train_size=0.8, rolling_window=60, scale=True):
        try:
            log_config.add_separator()
            logging.info(f"Initializing web scraper")
            ind_scraper = IndustriesScraper('https://stockanalysis.com/stocks/')
            scraped_tb = ind_scraper.run_scraper()
        except:
            return 1
        for symbol in scraped_tb.symbol[4:]:
            try:
                stock = Stock(symbol)
                getattr(stock, fetch_type)()
                stock.prepare_train_test_sets(train_size, rolling_window, scale=scale)
                base_for_model = Model(stock)
                base_for_model.lstm_nn(viz=False)
                logging.info(f"Successfully run framework for symbol {symbol}")
            except Exception as e:
                print(e)
                print(f'Process aborted for symbol {symbol}')
                pass

def main():
    Runner.run()
    
if __name__ == '__main__':
    main()