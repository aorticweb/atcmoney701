import os
from logging import getLogger
from typing import Dict

import requests
from requests import Response

from providers.client import Client as BaseClient
from providers.common.currency import Currency
from providers.common.quote import Quote
from providers.exception import ConfigException, ProviderAPIError

logger = getLogger(__name__)


class Client(BaseClient):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def _get(self, endpoint, params: Dict) -> Response:
        params = {**params, "apikey": self.api_key}
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params)
        except Exception as ex:
            logger.warning(f"Unexpected vantage Provider API call failure {ex}")
            raise ProviderAPIError(message="Market Provider call failure")

        return response

    def get_quote(self, symbol: str) -> Quote:
        response = self._get("/query", {"function": "GLOBAL_QUOTE", "symbol": symbol})
        if response.status_code > 299:
            raise ProviderAPIError(
                response=response,
                message=f"Market Provider call failure {response.status_code=}, {response.text=}",
            )
        try:
            response_data = response.json()
        except ValueError:
            raise ProviderAPIError(
                response=response,
                message=f"Market Provider call failure, response data is not json serializable {response.text=}",
            )

        value = response_data.get("Global Quote", {}).get("05. price", None)
        if value is None:
            raise ProviderAPIError(
                response=response,
                message=f"Market Provider call failure, response data does not contain price data {response_data=}",
            )

        return Quote(float(value), Currency.USD)


def get_vantage_client() -> BaseClient:
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    base_url = os.environ.get("ALPHA_VANTAGE_URL")
    if api_key is None or base_url is None:
        raise ConfigException(
            f"Incomplete vantage configuration api_key: {'*****' if api_key else 'MISSING'}"
            + f" base_url: {base_url if base_url else 'MISSING'}"
        )

    return Client(api_key, base_url)
