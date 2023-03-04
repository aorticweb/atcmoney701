#!/usr/bin/python
from logging import getLogger
from os import PathLike
from typing import List, Optional

import click
from atcmoney_cli.config import create_config_dir, load_env

from libs.providers import ClientFactory, ClientType
from libs.providers.client import Client
from libs.providers.exception import ProviderAPIError

MAX_QUOTE_CALL = 5
logger = getLogger("ATCMONEY")


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "-c",
    "--config-folder-path",
    default=None,
    help="Path to .atcmoney file, default is $HOME",
)
def init(config_folder_path: Optional[PathLike] = None):
    create_config_dir(config_folder_path)
    load_env(config_folder_path)


def print_quote(symbol: str, provider: Client):
    try:
        quote = provider.get_quote(symbol)
        click.echo(f"{symbol}: {quote.price} {quote.currency}")
    except ProviderAPIError as ex:
        logger.warning(ex.message)


@click.command()
@click.option(
    "-c",
    "--config-folder-path",
    default=None,
    help="Path to .atcmoney file, default is $HOME",
)
@click.argument("symbols", nargs=-1)
def quote(symbols: List[str], config_folder_path: Optional[PathLike] = None):
    load_env(config_folder_path)
    if len(symbols) > MAX_QUOTE_CALL:
        logger.warning(
            f"No more than 10 symbols supported at a time, will skip symbols after {symbols[MAX_QUOTE_CALL]}"
        )

    provider_client = ClientFactory[ClientType.VANTAGE]()

    for symbol in symbols[:MAX_QUOTE_CALL]:
        print_quote(symbol, provider_client)


cli.add_command(init)
cli.add_command(quote)
