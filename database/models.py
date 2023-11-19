from database.connection import Base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import String, Column, Text, DateTime, Float
from datetime import datetime

# this Item model (table) stems from the Base class and has its properties 
# named in an object-oriented style

SCHEMA = "stocks"
    
class StockIndustries(Base):
    __tablename__ = "stock_industries"
    __table_args__ = {'schema': SCHEMA}
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    symbol = Column(String, nullable=False, primary_key=True)
    company = Column(Text)
    industry = Column(Text)
    marketcap = Column(String)

class StockInfo(Base):
    __tablename__ = "stock_info"
    __table_args__ = {'schema': SCHEMA}
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    symbol = Column(String, nullable=False, primary_key=True)
    name = Column(Text)
    exchange = Column(String)
    assettype = Column(String)
    ipodate = Column(DateTime)
    delistingdate = Column(DateTime)
    status = Column(String)

class StockMerge(Base):
    __tablename__ = "stock_merged"
    __table_args__ = {'schema': SCHEMA}
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    symbol = Column(String, nullable=False, primary_key=True)
    companyname = Column(Text)
    exchange = Column(String)
    status = Column(String)
    ipodate = Column(DateTime)
    industry = Column(Text)
    marketcap = Column(String)

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
