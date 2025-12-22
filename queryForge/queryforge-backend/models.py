
from sqlalchemy import Table, Column, Integer, String, Date, MetaData, TIMESTAMP
from db import database

metadata = MetaData()

crypto_queries = Table(
    "crypto_queries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("symbol", String(10)),
    Column("start_date", Date),
    Column("end_date", Date),
    Column("created_at", TIMESTAMP),
)

stock_queries = Table(
    "stock_queries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("symbol", String(10)),
    Column("start_date", Date),
    Column("end_date", Date),
    Column("created_at", TIMESTAMP),
)