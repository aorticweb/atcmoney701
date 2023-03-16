from enum import Enum
from typing import Callable, Dict

from libs.providers.client import Client as BaseClient
from libs.providers.mock.client import get_mock_client  # noqa
from libs.providers.vantage.client import get_vantage_client  # noqa

ClientGenerator = Callable[[], BaseClient]


class ClientType(str, Enum):
    VANTAGE = "VANTAGE"
    MOCK = "MOCK"


ClientFactory: Dict[ClientType, ClientGenerator] = {
    ClientType.VANTAGE: get_vantage_client,
    ClientType.MOCK: get_mock_client,
}
