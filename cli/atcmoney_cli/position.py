import json
from json import JSONDecodeError
from typing import Dict, List, Optional

import click
import inquirer
from atcmoney_cli.config import get_provider, position_store_file
from atcmoney_cli.logging import logger

from libs.common.currency import Currency
from libs.common.position import Position
from libs.common.quote import Quote
from libs.common.trade import Side, Trade
from libs.providers.exception import ProviderAPIError


def dollar_precision(value: float) -> float:
    return round(value, 2)


@click.group(invoke_without_command=True)
@click.pass_context
def position(ctx):
    if ctx.invoked_subcommand is None:
        for position in load_positions():
            print_dict(_position_print_data(position))


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
    if position.currency == quote.currency:
        data[
            "absolute gains"
        ] = f"{dollar_precision(position.quantity * quote.price - position.cost)} {position.currency}"
        data[
            "relative gain"
        ] = f"{round(100 * (position.quantity * quote.price - position.cost)/position.cost, 6) }%"

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
        logger.warning(f"No position found for {symbol=}")

    try:
        quote = get_provider().get_quote(symbol)
    except ProviderAPIError as ex:
        logger.warning(ex.message)
        print_dict(_position_print_data(positions_map[symbol]))
        return

    print_dict(_position_details_print_data(positions_map[symbol], quote))


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def _register_trade(side: Side):
    questions = [
        inquirer.Text(
            "symbol",
            message="What is the instrument symbol?",
        ),
        inquirer.Text(
            "quantity",
            message=f"How many units are you {side.lower()}ing?",
            validate=lambda _, x: isfloat(x) and float(x) > 0,
        ),
        inquirer.Text(
            "unit_price",
            message="What is the price?",
            validate=lambda _, x: isfloat(x) and float(x) >= 0,
        ),
        inquirer.List(
            "total_or_unit_price",
            message="Is this the Total or Unit price?",
            choices=["Total", "Unit"],
        ),
        inquirer.List(
            "currency",
            message="What is the currency?",
            choices=[currency.name for currency in Currency],
        ),
    ]
    input_data = inquirer.prompt(questions)
    if input_data is None:
        return

    if side == Side.SELL:
        input_data["quantity"] = (-1) * float(input_data["quantity"])

    positions_map = load_positions_map()
    position = positions_map.get(input_data["symbol"])

    if input_data["total_or_unit_price"] == "Total":
        trade = Trade(**input_data, side=side)
    else:
        trade = Trade(**input_data, side=side)

    if position is None:
        try:
            get_provider().get_quote(input_data["symbol"])
        except ProviderAPIError as ex:
            logger.warning(ex.message)
            click.echo("Market Provider failed to find quote, aborting trade")
            return
        position = Position(
            quantity=trade.quantity,
            cost=trade.total_cost,
            symbol=trade.symbol,
            currency=trade.currency,
        )
    else:
        position.quantity += trade.quantity
        position.cost += trade.total_cost

    if position.quantity == 0:
        del positions_map[input_data["symbol"]]
    else:
        positions_map[input_data["symbol"]] = position
    store_positions(list(positions_map.values()))


@click.command(name="buy")
def register_buy():
    _register_trade(Side.BUY)


@click.command(name="sell")
def register_sell():
    _register_trade(Side.SELL)


position.add_command(details)
position.add_command(register_buy)
position.add_command(register_sell)
