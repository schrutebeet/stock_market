from database.connection import Base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import String, Column, Text, DateTime, Float, Date
from datetime import datetime

# this Item model (table) stems from the Base class and has its properties 
# named in an object-oriented style

SCHEMA = "stocks"

class Nasdaq(Base):
    __tablename__ = "nasdaq_securities"
    __table_args__ = {'schema': SCHEMA}
    timestamp = Column(TIMESTAMP, nullable=False)
    source_time = Column(TIMESTAMP, nullable=False)
    registration_date = Column(Date, nullable=False, primary_key=True)
    symbol =  Column(String, nullable=False, primary_key=True)
    security_name = Column(String)
    market_category = Column(String)
    test_issue = Column(String)
    financial_status = Column(String)
    round_lot_size = Column(String)
    is_etf = Column(String)
    nextshares = Column(String)
    industry = Column(String)
    sector = Column(String)

class Other(Base):
    __tablename__ = "other_securities"
    __table_args__ = {'schema': SCHEMA}
    timestamp = Column(TIMESTAMP, nullable=False)
    source_time = Column(TIMESTAMP, nullable=False)
    registration_date = Column(Date, nullable=False, primary_key=True)
    symbol = Column(String, nullable=False, primary_key=True)
    security_name = Column(String)
    exchange = Column(String)
    cqs_symbol = Column(String)
    is_etf = Column(String)
    round_lot_size = Column(String)
    test_issue = Column(String)
    nasdaq_symbol = Column(String)
    industry = Column(String)
    sector = Column(String)

def create_dynamic_model(class_name, model_name, schema_name, column_data):
    # Define the attributes for the class
    class_attributes = {
        "__tablename__": model_name,
        "__table_args__": {'schema': schema_name}
    }

    # Add columns to the class attributes
    for column_name, column_type in column_data.items():
        class_attributes[column_name] = column_type

    # Create the class using the type function
    dynamic_class = type(class_name, (Base,), class_attributes)
    return dynamic_class
