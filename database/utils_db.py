import inspect
from typing import List, Any, Union
import logging
import math

import sqlalchemy 
import pandas as pd
from database.connection import engine
from database import models
from database.models import create_dynamic_model
from database.connection import SessionLocal


class UtilsDB:
    def __init__(self) -> None:
        self.engine = engine
        self.dbsession = SessionLocal()

    def create_specific_model(self, class_name: str, model_name: str, schema_name: str, column_data: dict) -> object:
        """Create specific model inside specific schema.

        Args:
            class_name (str): Name of the class. Must be camel case - e.g.: 'AAPLDaily'. 
            model_name (str): Name of the model. Must be snake case - e.g.: 'aapl_daily'. 
            schema_name (str): Name of the schema where the model will be hosted.
            column_data (dict): Dictionary containing information on model columns: name, type, if primary key.
                                It must be of the type {'col1': Column(type, ...), 
                                                        'col2': Column(type, ...), 
                                                        'col3': Column(type, ...),
                                                         ...}

        Returns:
            object: Returns model class.
        """
            # Define the attributes for the class
        model_class = create_dynamic_model(class_name, model_name, schema_name, column_data)
        table_name = model_class.__tablename__
        schema_name = model_class.__table_args__["schema"]
        insp = sqlalchemy.inspect(self.engine)
        if not insp.has_table(table_name=table_name, schema=schema_name):
            model_class.__table__.create(self.engine)
            logging.info(f"Model '{model_name}' created successfully in schema '{schema_name}'.")
        return model_class

    def create_new_models(self) -> None:
        """Create all models found in database.models module, in case one of them is missing.
        """
        model_list = self.__get_all_classes("database.models")
        insp = sqlalchemy.inspect(self.engine)
        for cls in model_list:
            table_name = cls.__tablename__
            schema_name = cls.__table_args__["schema"]
            if not insp.has_table(table_name=table_name, schema=schema_name):
                cls.__table__.create(self.engine)
                logging.info(f"Model '{table_name}' created successfully in schema '{schema_name}'.")

    @staticmethod
    def __get_all_classes(model_name: str) -> List[Any]:
        """Get a list with all models defined in the _model_name_ module."""
        all_items = inspect.getmembers(models)
        classes = [
            item[1] for item in all_items if inspect.isclass(item[1]) and item[1].__module__ == model_name
        ]
        return classes
    
    def get_model_class_with_name(self, table_name: str) -> object:
        model_list = self.__get_all_classes("database.models")
        for cls in model_list:
            if cls.__tablename__ == table_name:
                objective_cls = cls
        return objective_cls

    def insert_df_in_db(self, df: pd.DataFrame, model: object, batch_size: int = 100_000) -> None:
        """Insert the input dataframe in the corresponding model in DB.

        Args:
            df (pd.DataFrame): Input dataframe of which its information will be stored in the DB.
            model (object): Model class with table characteristics.
            batch_size (int, optional): Maximum rows to be inserted into the DB per iteration. Defaults to 100_000.
        """
        batched_dfs = self._divide_df_in_batches(df, batch_size)
        logging.info(f"Starting data storage in DB for table '{model.__tablename__}'.")
        for df_ in batched_dfs:
            # argument "orient='records'" especifies the dictionary should be made row-wise
            dictionary_rows = df_.to_dict(orient='records')
            self.dbsession.bulk_insert_mappings(model, dictionary_rows)
        # Commit the changes to the database for each model
        self.dbsession.commit()
        logging.info(f"Table '{model.__tablename__}' has been successfully stored in DB.")
        # Close connection
        self.dbsession.close()

    @staticmethod
    def _divide_df_in_batches(input_df: pd.DataFrame, batch_size: int) -> List[pd.DataFrame]:
        """Divide dataframe in smaller pieces for speed improvement.
        """
        n_chunks = math.ceil(len(input_df) / batch_size)
        batched_df = []
        starting_row, ending_row = 0, batch_size
        for n in range(n_chunks):
            chunked_df = input_df.iloc[starting_row : ending_row, ]
            batched_df.append(chunked_df)
            starting_row += batch_size
            ending_row += batch_size
        return batched_df
