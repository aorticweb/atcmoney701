from enum import Enum
from typing import Dict

from pydantic import BaseModel

from libs.common.currency import Currency


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Trade(BaseModel):
    symbol: str
    side: Side
    currency: Currency
    quantity: float
    unit_price: float

    @classmethod
    def from_total_cost(cls, data: Dict, total_cost: float) -> "Trade":
        data["unit_price"] = total_cost / data["quantity"]
        return cls(**data)

    @property
    def total_cost(self) -> float:
        return self.unit_price * self.quantity
