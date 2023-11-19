from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import String, Column, Text, DateTime, Float

default_daily = {
    "timestamp":Column(TIMESTAMP(timezone=True)),
    "datetime": Column(TIMESTAMP, nullable=False, primary_key=True),
    "open": Column(Float),
    "high": Column(Float),
    "low": Column(Float),
    "close": Column(Float),
    "adj_close": Column(Float),
    "volume": Column(Float),
    "dividend_amount": Column(Float),
    "split_coeff": Column(Float),
    "symbol":  Column(String, primary_key=True),
}

default_minutes = {
    "timestamp":Column(TIMESTAMP(timezone=True)),
    "datetime": Column(TIMESTAMP, nullable=False, primary_key=True),
    "open": Column(Float),
    "high": Column(Float),
    "low": Column(Float),
    "close": Column(Float),
    "volume": Column(Float),
    "symbol":  Column(String, primary_key=True),
}