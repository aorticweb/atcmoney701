import os
from unittest import mock

import pytest
from atcmoney_cli.config import ATCMONEY_CONFIG_DIR_KEY


@pytest.fixture(autouse=True)
def mock_load_env():
    with mock.patch("atcmoney_cli.main.load_env") as mocked:
        os.environ[ATCMONEY_CONFIG_DIR_KEY] = "."
        yield mocked


@pytest.fixture(autouse=True)
def mock_file_system(fs):
    pass
