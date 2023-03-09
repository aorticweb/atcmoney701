import os
from logging import getLogger
from os import PathLike
from typing import Optional

from dotenv import load_dotenv

logger = getLogger("ATCMONEY")
ATCMONEY_CONFIG_DIR_KEY = "ATCMONEY_CONFIG_DIR"
DEFAULT_CONFIG_DIR = os.path.join(os.environ.get("HOME"), ".atcmoney")


# def create_config_dir(config_dir: Optional[PathLike] = None):
#     if config_dir is None:
#         config_dir = DEFAULT_CONFIG_DIR

#     if not os.path.exists(config_dir):
#         os.makedirs(config_dir)


def load_env(config_dir: Optional[PathLike] = None):
    if config_dir is None:
        config_dir = DEFAULT_CONFIG_DIR

    env_path = os.path.join(config_dir, ".env")
    if not os.path.exists(env_path):
        logger.info(f"Config file not found, creating config file {env_path}")
        open(env_path, "x")
    load_dotenv(env_path)
    os.environ[ATCMONEY_CONFIG_DIR_KEY] = config_dir


def position_store_file():
    return os.path.join(os.environ[ATCMONEY_CONFIG_DIR_KEY], ".positions.json")
