from typing import Optional, Tuple

from pydantic import BaseModel

from libs.common.currency import Currency
from libs.common.trade import PnL, Side, Trade


class Position(BaseModel):
    """Data model for an asset position.

    A Sell/Short position has a negative quantity but a positive cost

    Args:
        quantity: the quantity of the asset involved in the trade i.e 1.5 stocks
        cost: the cost spent to acquire the position i.e 1000 USD
        symbol: the asset symbol i.e GOOGL
        currency: cost currency
    """

    quantity: float
    cost: float
    symbol: str
    currency: Currency

    @property
    def side(self) -> Side:
        """Determine trade side long(buy)/short(sell).

        Determine trade side long(buy)/short(sell)
        based on the position quantity sign since position should never have
        zero quantity.

        Returns:
            the side of the Position
        """
        if self.quantity < 0:
            return Side.SELL
        return Side.BUY

    @property
    def unit_price(self) -> float:
        """Return position unit price.

        Returns
            The unit price for the asset held in the position
        """
        return self.cost / self.quantity

    def calculate_pnl(self, unit_price: float, quantity: Optional[float] = None) -> PnL:
        """Return the theoretical PnL from an incoming trade with a specific price.

        Args:
            unit_price: the price per unit of asset of the potential incoming trade
            quantity: the quantity of asset of the potential incoming trade, if None, the entire
                position quantity will be liquidated

        Returns:
            The trade PnL

        Raises:
            ValueError if the incoming quantity is greater than the trade quantity
        """
        if quantity is None:
            quantity = self.quantity
        sign = int(self.quantity / abs(self.quantity))
        quantity = abs(quantity)
        if quantity > abs(self.quantity):
            raise ValueError(
                "Incoming quantity cannot be greater than position quantity"
            )
        absolute_gains = (
            quantity * (unit_price - (self.cost / abs(self.quantity))) * sign
        )
        relative_gains = absolute_gains * abs(self.quantity) / (self.cost * quantity)
        return PnL(absolute_gains=absolute_gains, relative_gains=relative_gains)


def add_trade_to_position(
    trade: Trade, position: Optional[Position] = None
) -> Tuple[Optional[Position], Optional[PnL]]:
    """Create/Update position using trade to position

    Trust or do the math

    Args:
        trade: incoming trade
        position: potentially pre-existing position for symbol

    Returns:
        A tuple (position, pnl) containing the created/updated position if the position was not liquidated otherwise
        None and the profit/loss from the trade if the trade is in the opposite direction of the
        position otherwise None.
    """
    # new position
    if position is None:
        return (
            Position(
                quantity=trade.quantity,
                cost=trade.total_cost,
                symbol=trade.symbol,
                currency=trade.currency,
            ),
            None,
        )

    # increase position
    if trade.side == position.side:
        position.quantity += trade.quantity
        position.cost += trade.total_cost
        return position, None

    # position is switiching from buy to sell or sell to buy
    if abs(trade.quantity) > abs(position.quantity):
        pnl = position.calculate_pnl(trade.unit_price)
        return (
            Position(
                quantity=trade.quantity - position.quantity,
                cost=trade.unit_price * (trade.quantity - position.quantity),
                symbol=trade.symbol,
                currency=trade.currency,
            ),
            pnl,
        )

    pnl = position.calculate_pnl(trade.unit_price, trade.quantity)
    # position is liquidated
    if abs(trade.quantity) == abs(position.quantity):
        return None, pnl

    # partial position exposure reduction
    position.cost += trade.quantity * position.unit_price
    position.quantity += trade.quantity
    return position, pnl
