from logging import getLogger
from random import randint
from typing import Optional

from libs.common.currency import Currency
from libs.common.quote import Quote
from libs.providers.client import Client as BaseClient

logger = getLogger(__name__)


class Client(BaseClient):
    quote_value: Optional[float] = None
    exception: Optional[Exception] = None

    @classmethod
    def set_quote_value(cls, value: Optional[float] = None):
        cls.quote_value = value

    @classmethod
    def set_exception(cls, exc: Optional[Exception] = None):
        cls.exception = exc

    def __init__(self):
        pass

    def get_quote(self, _: str) -> Quote:
        if self.exception is not None:
            exception = self.exception
            self.set_exception(None)
            raise exception

        if self.quote_value is not None:
            value = self.quote_value
            self.set_quote_value(None)
            return Quote(float(value), Currency.USD)

        return Quote(float(randint(0, 1000)), Currency.USD)


def get_mock_client() -> BaseClient:
    return Client()
