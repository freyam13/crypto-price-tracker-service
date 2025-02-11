from sqlalchemy import Column, DateTime, Float, MetaData, String, Table

metadata = MetaData()

price_history = Table(
    "price_history",
    metadata,
    Column("pair", String, nullable=False),
    Column("price", Float, nullable=False),
    Column("timestamp", DateTime(timezone=True), nullable=False),
)
