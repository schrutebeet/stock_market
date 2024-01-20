"""
PACKAGES
"""
import random
import requests
import pandas as pd
from io import StringIO
import re
from datetime import datetime
from typing import List, Any

import yfinance as yf

from utils.headers import headers
from config.log_config import logger
from database.utils_db import UtilsDB
from database.models import Nasdaq, Other
from utils.rename_columns import rename_sec_columns

"""
VARIABLES
"""


class GeneralInformation:
    """Class for fetching information on most securities traded in the USA. Information includes the symbol,
       security name, financial status, industry and sector, among others.
    """

    def __init__(self) -> None:
        pass

    def run_extraction(self, securities_filter: List[str] = ['nasdaq', 'other']) -> pd.DataFrame:
        """Run all methods sequentially to get the joint results of all scrapings.

        Returns:
            pd.DataFrame: Dataframe containing information on different assets, as well as 
                          their industry group.
        """
        list_of_dfs = self.extract_securities(securities_filter = securities_filter)
        list_of_dfs_with_ind_sect = self._extract_industries_sectors(list_of_dfs)
        self.save_tables(list_of_dfs_with_ind_sect)
        joint_df_with_ind_sect = pd.concat(list_of_dfs_with_ind_sect)
        return joint_df_with_ind_sect

    def extract_securities(self, securities_filter: List[str] = ['nasdaq', 'other']) -> List[pd.DataFrame]:
        """Fetch stock information from www.nasdaqtrader.com. Such information is divided into 
        'NASDAQ-Listed Securities' and 'Other Exchange-Listed Securities'.

        Args:
            securities_filter (str): Ask for any specific type of securities. It can be ['nasdaq'], 
            ['other'] or ['nasdaq', 'other'].
        
        Returns:
            pd.DataFrame: Dataframe with general information on different securities.
        """
        list_of_dfs = []
        if 'nasdaq' in securities_filter:
            nasdaq_securities = self._call_api_for_specific_security('nasdaq', Nasdaq)
            nasdaq_stocks = nasdaq_securities[nasdaq_securities['is_etf'] == 'N'].iloc[:]
            nasdaq_stocks.metadata = nasdaq_securities.metadata
            list_of_dfs.append(nasdaq_stocks)
        if 'other' in securities_filter:
            other_securities = self._call_api_for_specific_security('other', Other)
            other_stocks = other_securities[other_securities['is_etf'] == 'N'].iloc[:]
            other_stocks.metadata = other_securities.metadata
            list_of_dfs.append(other_stocks)
        return list_of_dfs
    
    def _call_api_for_specific_security(self, security_group_name: str, model: Any) -> pd.DataFrame:
        """Request data information from the NASDAQ API. 

        Args:
            security_group_name (str): Two security group names are allowed: 
                                        - nasdaq: for those securities traded in a NASDAQ index.
                                        - other: For all other securities traded in the USA.
            model (Any): Object containing the DB table structure for PostgreSQL.

        Returns:
            pd.DataFrame: API response, made dataframe.
        """
        response = requests.get(f"http://ftp.nasdaqtrader.com/dynamic/SymDir/{security_group_name}listed.txt", 
                                headers=random.choice(headers))
        corpus = response.text
        df = pd.read_csv(StringIO(corpus), sep="|")
        df = df.rename(columns=rename_sec_columns)
        df = df.dropna(subset=['symbol'])
        last_row_first_col = df.iloc[-1, 0]
        if 'File Creation Time:' in last_row_first_col:
            pattern = r'(\d+:\d+)'
            match = re.search(pattern, last_row_first_col)
            str_timestamp = match.group(1)
            format_string = "%m%d%Y%H:%M"
            date_object = datetime.strptime(str_timestamp, format_string) 
            df = df.drop(df.index[-1])
        else:
            date_object = None
        metadata = {'name': security_group_name.capitalize(), 'creation_date': date_object, 'model': model}
        df.metadata = metadata
        return df

    def _extract_industries_sectors(self, list_of_securities: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """Extract the industry and sector of each of the rows (ETFs) in the dataframe.
           If symbol is an ETF, not industry nor sector is given.

        Args:
            list_of_securities (List[pd.DataFrame]): List of dataframes with symbols from which to fetch their 
                                                     industry and sector.

        Returns:
            List[pd.DataFrame]: Same list of dataframes as input but with "industry" and "sector" as extra columns.
        """
        for sec in list_of_securities:
            industry_list, sector_list = [], []
            for symbol in sec['symbol']:
                if sec[sec['symbol'] == symbol].iloc[0]['is_etf'] == 'N':
                    try:
                        info = yf.Ticker(symbol.replace(".", "-")).info
                        industry_list.append(info.get('industry', 'N/A'))
                        sector_list.append(info.get('sector', 'N/A'))
                    except requests.exceptions.HTTPError:
                        industry_list.append(None)
                        sector_list.append(None)
                        logger.debug(f"Request returned an HTTP error. "\
                                     f"No industry nor sector was found for {symbol}.")
                    except requests.exceptions.ChunkedEncodingError:
                        industry_list.append(None)
                        sector_list.append(None)
                        logger.debug(f"Connection broken. "\
                                     f"No industry nor sector was found for {symbol}.")
                else:
                    industry_list.append(None)
                    sector_list.append(None)
                    logger.debug(f"Symbol is an ETF. "\
                                f"No industry nor sector was applied for {symbol}.")
            sec['industry'] = industry_list
            sec['sector'] = sector_list
        return list_of_securities
    
    def save_tables(self, dfs_list: List[pd.DataFrame]) -> None:
        """Save any list of dataframes into the DB. A previous model with the data 
           types of the table is needed.

        Args:
            dfs_list (List[pd.DataFrame]): Pandas dataframes to be stored in the DB.
        """
        save_tables_in_db = UtilsDB()
        save_tables_in_db.create_new_models()
        for df in dfs_list:
            df['source_time'] = df.metadata['creation_date']
            _time = datetime.now()
            df['timestamp'] = _time
            df['registration_date'] = _time.strftime("%Y-%m-%d")
            save_tables_in_db.insert_df_in_db(df, df.metadata['model'], batch_size=5_000)
