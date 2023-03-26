from pydantic_factories import ModelFactory

from libs.common.position import Position
from libs.common.quote import Quote
from libs.common.trade import Trade


class PositionFactory(ModelFactory):
    __model__ = Position


class QuoteFactory(ModelFactory):
    __model__ = Quote


class TradeFactory(ModelFactory):
    __model__ = Trade
