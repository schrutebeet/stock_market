import inspect
from typing import List, Any

import sqlalchemy 
from database.connection import engine
from database import models


class UtilsDB:
    def __init__(self) -> None:
        self.engine = engine

    def create_new_models(self):
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


UtilsDB().create_new_models()
