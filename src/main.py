import copy

import config.log_config as log_config
from config.log_config import logger
from src.general_information import GeneralInformation
from src.stock import Stock
from database.utils_db import UtilsDB
from utils.dafault_columns import default_daily, default_minutes
from src.email_notifications.email_generator import EmailGenerator

def main():
    log_config.add_separator()
    logger.info(f"Initializing information scraping.")
    # Call API with metadata on stocks (industry-type, company name, exchange market...)
    # After fetching, automatically store data in DB
    stock_df = GeneralInformation().run_extraction()
    utils_db = UtilsDB()
    stock_dictionary = {}
    for symbol in stock_df.symbol[:]:
        logger.debug(f"Checking additional information for symbol {symbol}.")
        # initiation the stock class for particular stock
        stock_dictionary[f"{symbol}"] = Stock(symbol)
        # Fetching OHLCV data on that stock
        stock_extractor = stock_dictionary[f"{symbol}"].extractor
        stock_dictionary[f"{symbol}_daily"] = stock_extractor.get_data(lookback_period = 2, chunk_size = 2, interval="1d")
        stock_dictionary[f"{symbol}_1min"] = stock_extractor.get_data(lookback_period = 2, chunk_size = 2, interval="1m")

    for symbol in stock_df.symbol[:]:
        model_daily = utils_db.create_specific_model(class_name=f"{symbol}_daily", model_name=f"{symbol}_daily", 
                                                        schema_name="daily_quotes", column_data=copy.deepcopy(default_daily))
        model_minute = utils_db.create_specific_model(class_name=f"{symbol}_1min", model_name=f"{symbol}_1min", 
                                                        schema_name="onemin_quotes", column_data=copy.deepcopy(default_minutes))
        # Store daily data in DB
        utils_db.insert_df_in_db(stock_dictionary[f"{symbol}_daily"], model_daily)
        utils_db.insert_df_in_db(stock_dictionary[f"{symbol}_1min"], model_minute)

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
    email = EmailGenerator()
    email_info =  {'recipient': 'Ricardo', 'n_stocks': len(stock_df.symbol)}
    email.send_successful_app_run(email_info)


if __name__ == "__main__":
    main()
