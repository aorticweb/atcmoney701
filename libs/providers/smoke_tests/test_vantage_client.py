import pytest
from providers import ClientFactory, ClientType

from libs.common.currency import Currency
from libs.common.quote import Quote
from libs.providers.exception import ProviderAPIError

client_generator = ClientFactory[ClientType.VANTAGE]


def test_get_quote():
    """
    Test getting a quote from vantage
    """
    client = client_generator()
    quote = client.get_quote("GOOGL")
    assert isinstance(quote, Quote)
    assert quote.currency == Currency.USD
    assert isinstance(quote.price, float)


def test_get_quote_fake_symbol_raises_error():
    """
    Test getting a quote from vantage
    """
    client = client_generator()
    with pytest.raises(ProviderAPIError):
        client.get_quote("BAD_SYMBOL_INVALID")
