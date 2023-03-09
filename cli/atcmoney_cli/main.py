#!/usr/bin/python
from os import PathLike
from typing import Optional

import click
from atcmoney_cli.config import load_env
from atcmoney_cli.position import position
from atcmoney_cli.quote import quote


@click.group()
@click.option(
    "-c",
    "--config-folder-path",
    default=None,
    help="Path to .atcmoney file, default is $HOME",
)
def cli(config_folder_path: Optional[PathLike] = None):
    load_env(config_folder_path)


cli.add_command(quote)
cli.add_command(position)
