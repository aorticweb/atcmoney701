from enum import Enum

from pydantic import BaseModel, confloat

from libs.common.currency import Currency


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Trade(BaseModel):
    """Data model for trade.

    This is the core (minimum) information required for a trade.
    This is purposefuly kept simple to accomodate multiple types of
    assets. Symbol could be replaced with identifier.

    Args:
        symbol: the asset symbol i.e GOOGL
        side: buy/sell enum
        currency: unit price currency
        quantity: the quantity of the asset involved in the trade i.e 1.5 stocks
        unit_price: trade asset unit price i.e for one unit of quantity
    """

    symbol: str
    side: Side
    currency: Currency
    quantity: float
    unit_price: confloat(ge=0)

    @property
    def total_cost(self) -> float:
        """Return nominal cost of the trade.

        Returns:
            the cost of the trade
        """
        return self.unit_price * self.quantity


class PnL(BaseModel):
    """Profit and Loss of a Trade

    Args:
        absolute_gains: nominal gains from trade(s)
        relative_gains: relative (%) gains from trade(s)
        unit_price: asset unit_price
    """

    absolute_gains: float
    relative_gains: float
