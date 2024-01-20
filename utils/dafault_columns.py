from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import String, Column, Text, DateTime, Float

default_daily = [
    Column("timestamp", TIMESTAMP(timezone=True)),
    Column("timestamp_day", TIMESTAMP(timezone=True)),
    Column("datetime", TIMESTAMP, nullable=False, primary_key=True),
    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
    Column("adj_close", Float),
    Column("volume", Float),
    Column("symbol", String, primary_key=True),
]

default_minutes = [
    Column("timestamp", TIMESTAMP(timezone=True)),
    Column("timestamp_day", TIMESTAMP(timezone=True)),
    Column("datetime", TIMESTAMP, nullable=False, primary_key=True),
    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
    Column("volume", Float),
    Column("symbol", String, primary_key=True),
]