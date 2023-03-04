from typing import Optional

from requests import Response


class ProviderAPIError(Exception):
    def __init__(
        self, response: Optional[Response] = None, message: Optional[str] = None
    ):
        self.response = response
        self.message = message


class ConfigException(Exception):
    pass
