from pydantic import BaseModel

from libs.common.currency import Currency


class Position(BaseModel):
    class Config:
        use_enum_values = True

    quantity: float
    cost: float
    symbol: str
    currency: Currency
