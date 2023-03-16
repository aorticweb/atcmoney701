from typing import List

import click
from atcmoney_cli.config import get_provider
from atcmoney_cli.logging import logger

from libs.providers.client import Client
from libs.providers.exception import ProviderAPIError

MAX_QUOTE_CALL = 5


def print_quote(symbol: str, provider: Client):
    try:
        quote = provider.get_quote(symbol)
        click.echo(f"{symbol}: {quote.price} {quote.currency}")
    except ProviderAPIError as ex:
        logger.warning(ex.message)


@click.command()
@click.argument("symbols", nargs=-1)
def quote(symbols: List[str]):
    if len(symbols) > MAX_QUOTE_CALL:
        logger.warning(
            f"No more than {MAX_QUOTE_CALL} symbols supported "
            + f"at a time, will skip symbols after {symbols[MAX_QUOTE_CALL]}"
        )

    for symbol in symbols[:MAX_QUOTE_CALL]:
        print_quote(symbol, get_provider())
