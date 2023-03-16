import pytest

from libs.common.currency import Currency
from libs.common.quote import Quote
from libs.providers import ClientFactory, ClientType
from libs.providers.exception import ProviderAPIError
from libs.providers.mock.client import Client

client_generator = ClientFactory[ClientType.MOCK]


def test_correct_instance():
    assert isinstance(client_generator(), Client)


def test_get_quote():
    """
    Test getting a quote from mock client
    """
    client = client_generator()
    quote = client.get_quote("GOOGL")
    assert isinstance(quote, Quote)
    assert quote.currency == Currency.USD
    assert isinstance(quote.price, float)


def test_get_quote_fake_symbol_raises_error():
    """
    Test getting a quote from mock client when class is set to return a mock Exception
    """
    client = client_generator()
    Client.set_exception(ProviderAPIError(message="Fake Provider error"))
    assert client.exception is not None
    with pytest.raises(ProviderAPIError):
        client.get_quote("GOOGL")


def test_get_quote_specific_value():
    """
    Test getting a quote from mock client when class is set to return a specific value
    """
    client = client_generator()
    Client.set_quote_value(10.0)
    quote = client.get_quote("GOOGL")
    assert isinstance(quote, Quote)
    assert quote.currency == Currency.USD
    assert isinstance(quote.price, float)
    assert quote.price == 10.0
