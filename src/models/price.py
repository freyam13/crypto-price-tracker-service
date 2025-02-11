from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Price(BaseModel):
    pair: str
    price: float
    timestamp: datetime

    class Config:
        from_attributes = True


class PriceHistory(BaseModel):
    pair: str
    prices: list[Price]
    volatility_rank: Optional[int] = None
