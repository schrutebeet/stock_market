import inspect
from typing import List, Any

import sqlalchemy 
from database.connection import engine
from database import models
from database.models import create_dynamic_model


class UtilsDB:
    def __init__(self) -> None:
        self.engine = engine

    def create_specific_model(self, class_name: str, model_name: str, schema_name: str, column_data: dict) -> None:
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
        """
            # Define the attributes for the class
        model_class = create_dynamic_model(class_name, model_name, schema_name, column_data)
        table_name = model_class.__tablename__
        schema_name = model_class.__table_args__["schema"]
        insp = sqlalchemy.inspect(self.engine)
        if not insp.has_table(table_name=table_name, schema=schema_name):
            model_class.__table__.create(self.engine)

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

    @staticmethod
    def __get_all_classes(model_name: str) -> List[Any]:
        """Get a list with all models defined in the _model_name_ module."""
        all_items = inspect.getmembers(models)
        classes = [
            item[1] for item in all_items if inspect.isclass(item[1]) and item[1].__module__ == model_name
        ]
        return classes
    
    def get_class_with_table_name(self, table_name: str) -> Any:
        model_list = self.__get_all_classes("database.models")
        for cls in model_list:
            if cls.__tablename__ == table_name:
                objective_cls = cls
        return objective_cls
