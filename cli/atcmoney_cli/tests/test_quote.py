"""Very basic tests for quote command mainly asserting that the commands all return status_code=0
"""
from atcmoney_cli.main import cli
from click.testing import CliRunner

from libs.providers.exception import ProviderAPIError
from libs.providers.mock.client import Client


def test_quote_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["quote", "--help"])
    assert result.exit_code == 0


def test_quote_success():
    runner = CliRunner()
    result = runner.invoke(cli, ["quote", "MSFT"])
    assert result.exit_code == 0


def test_quote_success_multi_symbols():
    runner = CliRunner()
    result = runner.invoke(cli, ["quote", "MSFT", "GOOGL"])
    assert result.exit_code == 0


def test_quote_provider_api_error():
    Client.set_exception(ProviderAPIError(message="Fake Provider error"))
    runner = CliRunner()
    result = runner.invoke(cli, ["quote", "MSFT", "GOOGL"])
    assert result.exit_code == 0
