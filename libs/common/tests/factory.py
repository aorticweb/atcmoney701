from pydantic_factories import ModelFactory

from libs.common.position import Position
from libs.common.quote import Quote
from libs.common.trade import Trade


class PositionFactory(ModelFactory):
    """Factory for Position pydantic model."""

    __model__ = Position


class QuoteFactory(ModelFactory):
    """Factory for Quote pydantic model."""

    __model__ = Quote


class TradeFactory(ModelFactory):
    """Factory for Trade pydantic model."""

    __model__ = Trade
