import json
from json import JSONDecodeError
from typing import Dict, List, Optional

import click
import inquirer
from atcmoney_cli.config import get_provider, position_store_file
from atcmoney_cli.logging import logger
from click.exceptions import BadParameter

from libs.common.currency import Currency
from libs.common.position import Position, add_trade_to_position
from libs.common.quote import Quote
from libs.common.trade import Side, Trade
from libs.providers.exception import ProviderAPIError


def dollar_precision(value: float) -> float:
    return round(value, 2)


@click.group(invoke_without_command=True)
@click.pass_context
def position(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Fetching positions")
        for position in load_positions():
            print_dict(_position_print_data(position))
        click.echo("Done Fetching positions")


def print_dict(data: Dict):
    print_pairs: List[str] = []
    for key, value in data.items():
        print_pairs.append(f"{key}: {value}")
    click.echo(", ".join(print_pairs))


def _position_print_data(position: Position) -> Dict:
    return {
        "symbol": position.symbol,
        "quantity": position.quantity,
        "cost": f"{dollar_precision(position.cost)} {position.currency}",
    }


def _position_details_print_data(position: Position, quote: Quote) -> Dict:
    data = _position_print_data(position)
    pnl = position.calculate_pnl(quote.price)
    if position.currency == quote.currency:
        data[
            "absolute gains"
        ] = f"{dollar_precision(pnl.absolute_gains)} {position.currency}"
        data["relative gain"] = f"{round(100 * pnl.relative_gains, 6) }%"

    data["current price"] = f"{quote.price} {quote.currency}"
    data[
        "current total value"
    ] = f"{dollar_precision(quote.price * position.quantity)} {quote.currency}"
    return data


def load_positions() -> List[Position]:
    try:
        positions = [
            Position(**position) for position in json.load(open(position_store_file()))
        ]
    except FileNotFoundError:
        logger.warning(
            f"Position data file did not exist, creating file in {position_store_file()}"
        )
        json.dump([], open(position_store_file(), "w"))
        return []
    except (ValueError, JSONDecodeError):
        logger.warning(f"Unreadable position data store: {position_store_file()}")
        return []
    return positions


def store_positions(positions: List[Position]):
    # This is silly but it converts a pydantic model to  a jsonable dictionary
    json.dump(
        [json.loads(position.json()) for position in positions],
        open(position_store_file(), "w"),
    )


def load_positions_map() -> Dict[str, Position]:
    return {position.symbol: position for position in load_positions()}


def user_select_from_stocks(symbols: List[str]) -> str:
    questions = [
        inquirer.List(
            "stock",
            message="Which stock do you want detail for?",
            choices=symbols,
        ),
    ]
    return inquirer.prompt(questions)["stock"]


@click.command()
@click.option(
    "-s",
    "--symbol",
    default=None,
    help="Position symbol to get details for",
)
def details(symbol: Optional[str] = None):
    positions_map = load_positions_map()
    if symbol is None:
        symbol = user_select_from_stocks([s for s in positions_map.keys()])

    if symbol not in positions_map.keys():
        click.echo(f"No position found for {symbol=}")
        return

    try:
        quote = get_provider().get_quote(symbol)
    except ProviderAPIError as ex:
        logger.warning(ex.message)
        print_dict(_position_print_data(positions_map[symbol]))
        return

    print_dict(_position_details_print_data(positions_map[symbol], quote))


def _register_trade(side: Side):
    """Helpers function to perform trade.

    Perform trade, print details and pnl and store position/updated position

    Args:
        side: whether the trade is a buy or a sell
    """

    def isfloat(num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def float_larger_than_zero(value):
        if isfloat(value) and float(value) > 0:
            return float(value)
        raise BadParameter(message="Must be float greater than zero")

    def float_larger_than_or_equal_zero(value):
        if isfloat(value) and float(value) >= 0:
            return float(value)
        raise BadParameter(message="Must be float greater than or equal zero")

    symbol = click.prompt("What is the instrument symbol?", type=str)
    quantity = click.prompt(
        f"How many units are you {side.lower()}ing?", value_proc=float_larger_than_zero
    )
    unit_price = click.prompt(
        "What is the price?", value_proc=float_larger_than_or_equal_zero
    )
    total_or_unit_price = inquirer.list_input(
        message="Is this the Total or Unit price?",
        choices=["Total", "Unit"],
    )
    currency = inquirer.list_input(
        message="What is the currency?",
        choices=[currency.name for currency in Currency],
    )

    if side == Side.SELL:
        quantity = (-1) * quantity

    positions_map = load_positions_map()
    position = positions_map.get(symbol)

    if total_or_unit_price == "Total":
        unit_price = unit_price / abs(quantity)

    trade = Trade(
        symbol=symbol,
        side=side,
        currency=currency,
        quantity=quantity,
        unit_price=unit_price,
    )

    if position is None:
        try:
            get_provider().get_quote(symbol)
        except ProviderAPIError as ex:
            logger.warning(ex.message)
            click.echo("Market Provider failed to find quote, aborting trade")
            return

    position, pnl = add_trade_to_position(trade, position)
    if pnl is not None:
        click.echo(
            f"absolute gains: {pnl.absolute_gains} {trade.currency},"
            + f" relative gains: {round(100 * pnl.relative_gains, 6) }%"
        )

    if position is None:
        del positions_map[symbol]
        click.echo("Position was liquidated")
    else:
        positions_map[symbol] = position
        click.echo(f"Position updated to {position.quantity} units")

    store_positions(list(positions_map.values()))


@click.command(name="buy")
def register_buy():
    """Command for position buy trade."""
    click.echo("Begining trdae registration...")
    _register_trade(Side.BUY)


@click.command(name="sell")
def register_sell():
    """Command for position sell trade."""
    _register_trade(Side.SELL)


position.add_command(details)
position.add_command(register_buy)
position.add_command(register_sell)
