from enum import Enum
from typing import Callable, Dict

from providers.client import Client as BaseClient
from providers.vantage.client import get_vantage_client  # noqa

ClientGenerator = Callable[[], BaseClient]


class ClientType(str, Enum):
    VANTAGE = "VANTAGE"


ClientFactory: Dict[ClientType, ClientGenerator] = {ClientType.VANTAGE: get_vantage_client}
