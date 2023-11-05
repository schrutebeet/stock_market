from database.connection import Base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import String, Column, Text, DateTime
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
