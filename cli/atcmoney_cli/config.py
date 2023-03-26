import os
from logging import getLogger
from os import PathLike
from typing import Optional

from dotenv import load_dotenv

from libs.providers import ClientFactory, ClientType
from libs.providers.client import Client

logger = getLogger("ATCMONEY")
ATCMONEY_CONFIG_DIR_KEY = "ATCMONEY_CONFIG_DIR"
ATCMONEY_PROVIDER = "ATCMONEY_PROVIDER"
DEFAULT_CONFIG_DIR = os.path.join(os.environ.get("HOME"), ".atcmoney")


def load_env(config_dir: Optional[PathLike] = None):
    """Load environment from config file into os.environ.

    Args:
        config_dir: the path to atcmney config dir

    """
    if config_dir is None:
        config_dir = DEFAULT_CONFIG_DIR

    env_path = os.path.join(config_dir, ".env")
    if not os.path.exists(env_path):
        logger.info(f"Config file not found, creating config file {env_path}")
        open(env_path, "x")
    load_dotenv(env_path)
    os.environ[ATCMONEY_CONFIG_DIR_KEY] = config_dir


def get_provider() -> Client:
    """Get data provider client.

    Returns:
        Provider client
    """
    return ClientFactory[os.environ.get(ATCMONEY_PROVIDER, ClientType.MOCK)]()


def position_store_file() -> str:
    """Get path to position store file.

    Returns:
        path to position store file
    """
    return os.path.join(os.environ[ATCMONEY_CONFIG_DIR_KEY], ".positions.json")
