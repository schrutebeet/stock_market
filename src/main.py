import copy
import time
import sys


import config.log_config as log_config
from config.log_config import logger
from src.models import Model
from src.scrape_industries import IndustriesScraper
from src.stock import Stock
from utils.util_funcs import timeit
from database.utils_db import UtilsDB
from utils.dafault_columns import default_daily, default_minutes

def main():
    log_config.add_separator()
    logger.info(f"Initializing information scraping.")
    # Scraping metadata on stocks (industry-type, company name, exchange market...)
    ind_scraper = IndustriesScraper("https://stockanalysis.com/stocks/")
    scraped_tb = ind_scraper.run_scraper()
    stock_dictionary = {}
    utils_db = UtilsDB()
    for symbol in scraped_tb.symbol[:10]:
        # initiation the stock class for particular stock
        stock_dictionary[f"{symbol}"] = Stock(symbol)
        # Fetching OHLCV data on that stock
        stock_extractor = stock_dictionary[f"{symbol}"].extractor
        stock_dictionary[f"{symbol}_daily"] = stock_extractor.get_data(period="daily")
        stock_dictionary[f"{symbol}_1min"] = stock_extractor.get_data(period="1min")
    
    for symbol in scraped_tb.symbol[:10]:
        model_daily = utils_db.create_specific_model(class_name=f"{symbol}_daily", model_name=f"{symbol}_daily", 
                                                        schema_name="daily_quotes", column_data=copy.deepcopy(default_daily))
        model_minute = utils_db.create_specific_model(class_name=symbol+"1min", model_name=symbol.lower()+"_1min", 
                                                        schema_name="onemin_quotes", column_data=copy.deepcopy(default_minutes))
        # Store daily data in DB
        utils_db.insert_df_in_db(stock_dictionary[f"{symbol}_daily"], model_daily)
        utils_db.insert_df_in_db(stock_dictionary[f"{symbol}_1min"], model_minute)

    # Commit the changes to the database for each model
    utils_db.dbsession.commit()
    # Close connection
    utils_db.dbsession.close()
            # Saving data in DB
            # utils_db = UtilsDB()
            # # Create daily and minute tables for particular stock (if they do not exist)
            # # deepcopy is needed so that no column is affected by previous tables
            # model_daily = utils_db.create_specific_model(class_name=symbol+"Daily", model_name=symbol.lower()+"_daily", 
            #                                                 schema_name="daily_quotes", column_data=copy.deepcopy(default_daily))
            # model_minute = utils_db.create_specific_model(class_name=symbol+"1min", model_name=symbol.lower()+"_1min", 
            #                                                 schema_name="onemin_quotes", column_data=copy.deepcopy(default_minutes))
            # # Store daily data in DB
            # if len(daily_data) > 0:
            #     utils_db.insert_df_in_db(daily_data, model_daily)
            # # Store minute data in DB
            # if len(minute_data) > 0:
            #     utils_db.insert_df_in_db(minute_data, model_minute)


            # getattr(stock, fetch_type)()
            # stock.prepare_train_test_sets(train_size, rolling_window, scale=scale)
            # base_for_model = Model(stock)
            # accuracy = base_for_model.lstm_nn(viz=False)
            # logger.info(f"Successfully run framework for symbol {symbol}. Score: {accuracy*100:.2f}%")
    logger.info("SUCCESS: END OF PROCESS")


if __name__ == "__main__":
    main()
