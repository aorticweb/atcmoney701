from libs.providers.common.quote import Quote


class Client:
    def get_quote(self, symbol: str) -> Quote:
        """Fetches current quote for symbol from the data provider.

        Args:
            symbol: Symbol/Ticker for the security.

        Returns:
            A live quote for the symbol

        Raises:
            ValueError: An error occurred while reading the response from the provider.
            ProviderAPIError: An error occured while fetching the live quote from the provider.
        """
        pass
