import pytest

from libs.common.currency import Currency
from libs.common.position import Position, add_trade_to_position
from libs.common.tests.factory import PositionFactory, TradeFactory
from libs.common.trade import Side, Trade


@pytest.fixture
def buy_trade():
    return Trade(
        symbol="GOOGL",
        side=Side.BUY,
        currency=Currency.USD,
        quantity=1.0,
        unit_price=10,
    )


@pytest.fixture
def sell_trade():
    return Trade(
        symbol="GOOGL",
        side=Side.BUY,
        currency=Currency.USD,
        quantity=1.0,
        unit_price=10,
    )


def test_add_trade_to_position_no_position_exists():
    trade: Trade = TradeFactory.build(side=Side.BUY, quantity=1.0, unit_price=10)
    position, pnl = add_trade_to_position(trade)

    assert pnl is None
    assert position is not None
    assert position.quantity == trade.quantity
    assert position.cost == trade.total_cost


def test_add_buy_trade_to_buy_position():
    trade: Trade = TradeFactory.build(side=Side.BUY, quantity=1.0, unit_price=10)
    position: Position = PositionFactory.build(quantity=1.0, cost=12)
    position_copy, pnl = add_trade_to_position(trade, position)

    assert pnl is None
    assert position_copy is not None
    assert position.quantity == 2.0
    assert position.cost == 22.0


def test_partial_liquidation_of_buy_position_with_profit():
    trade: Trade = TradeFactory.build(side=Side.SELL, quantity=-1.0, unit_price=15)
    position: Position = PositionFactory.build(quantity=20.0, cost=240)
    position_copy, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert position_copy is not None
    assert position.quantity == 19.0
    assert position.cost == 228
    assert pnl.absolute_gains == 3.0
    assert pnl.relative_gains == 3.0 / 12.0


def test_partial_liquidation_of_buy_position_with_loss():
    trade: Trade = TradeFactory.build(side=Side.SELL, quantity=-1.0, unit_price=10)
    position: Position = PositionFactory.build(quantity=20.0, cost=240)
    position_copy, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert position_copy is not None
    assert position.quantity == 19.0
    assert position.cost == 228
    assert pnl.absolute_gains == -2.0
    assert pnl.relative_gains == -2.0 / 12.0


def test_full_liquidation_of_buy_position_with_profit():
    trade: Trade = TradeFactory.build(side=Side.SELL, quantity=-20.0, unit_price=15)
    position: Position = PositionFactory.build(quantity=20.0, cost=240)
    position_copy, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert position_copy is None
    assert pnl.absolute_gains == 3.0 * 20.0
    assert pnl.relative_gains == 3.0 / 12.0


def test_full_liquidation_of_buy_position_with_profit_simple():
    trade: Trade = TradeFactory.build(side=Side.SELL, quantity=-1.0, unit_price=140)
    position: Position = PositionFactory.build(quantity=1.0, cost=100)
    position_copy, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert position_copy is None
    assert pnl.absolute_gains == 40.0
    assert pnl.relative_gains == 0.4


def test_full_liquidation_of_buy_position_with_loss():
    trade: Trade = TradeFactory.build(side=Side.SELL, quantity=-20.0, unit_price=10)
    position: Position = PositionFactory.build(quantity=20.0, cost=240)
    position_copy, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert position_copy is None
    assert pnl.absolute_gains == -2.0 * 20
    assert pnl.relative_gains == -2.0 / 12.0


def test_position_liquidation_buy_with_short_sale_with_gain():
    trade: Trade = TradeFactory.build(side=Side.SELL, quantity=-20.0, unit_price=300)
    position: Position = PositionFactory.build(quantity=10.0, cost=2400)
    new_position, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert new_position is not None
    assert new_position.quantity == trade.quantity - position.quantity
    assert new_position.cost == (trade.quantity - position.quantity) * trade.unit_price
    assert pnl.absolute_gains == 600
    assert pnl.relative_gains == 600 / 2400


def test_position_liquidation_buy_with_short_sale_with_loss():
    trade: Trade = TradeFactory.build(side=Side.SELL, quantity=-20.0, unit_price=240)
    position: Position = PositionFactory.build(quantity=10.0, cost=3000)
    new_position, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert new_position is not None
    assert new_position.quantity == trade.quantity - position.quantity
    assert new_position.cost == (trade.quantity - position.quantity) * trade.unit_price
    assert pnl.absolute_gains == -600
    assert pnl.relative_gains == -600 / 3000


def test_position_liquidation_sell_with_long_buy_with_loss():
    trade: Trade = TradeFactory.build(side=Side.BUY, quantity=20.0, unit_price=300)
    position: Position = PositionFactory.build(quantity=-10.0, cost=2400)
    new_position, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert new_position is not None
    assert new_position.quantity == trade.quantity - position.quantity
    assert new_position.cost == (trade.quantity - position.quantity) * trade.unit_price
    assert pnl.absolute_gains == -600
    assert pnl.relative_gains == -600 / 2400


def test_position_liquidation_sell_with_long_buy_with_gain():
    trade: Trade = TradeFactory.build(side=Side.BUY, quantity=20.0, unit_price=240)
    position: Position = PositionFactory.build(quantity=-10.0, cost=3000)
    new_position, pnl = add_trade_to_position(trade, position)

    assert pnl is not None
    assert new_position is not None
    assert new_position.quantity == trade.quantity - position.quantity
    assert new_position.cost == (trade.quantity - position.quantity) * trade.unit_price
    assert pnl.absolute_gains == 600
    assert pnl.relative_gains == 600 / 3000


def test_position_pnl_sell():
    position: Position = PositionFactory.build(quantity=-1.0, cost=300)
    pnl = position.calculate_pnl(280)
    assert pnl.absolute_gains == 20
    assert pnl.relative_gains == 20 / 300
