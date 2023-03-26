"""Very basic tests for position command mainly asserting that the commands all return status_code=0
"""
from unittest import mock

from atcmoney_cli.logging import logger
from atcmoney_cli.main import cli
from click.testing import CliRunner

from libs.providers.exception import ProviderAPIError
from libs.providers.mock.client import Client


def test_position_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["position", "--help"])
    assert result.exit_code == 0


def test_position_success():
    runner = CliRunner()
    result = runner.invoke(cli, ["position"])
    assert result.exit_code == 0


@mock.patch("inquirer.list_input")
def test_position_buy(mock_list_input):
    mock_list_input.side_effect = ["Total", "USD"]
    inputs = ["MSFT", "10", "150"]
    runner = CliRunner()
    result = runner.invoke(cli, ["position", "buy"], input="\n".join(inputs))
    logger.warning(str(result.output))
    assert result.exit_code == 0
    assert "Position updated to 10.0 units" in result.output


@mock.patch("inquirer.list_input")
def test_position_naked_sell(mock_list_input):
    mock_list_input.side_effect = ["Total", "USD"]
    inputs = ["MSFT", "10", "150"]
    runner = CliRunner()
    result = runner.invoke(cli, ["position", "sell"], input="\n".join(inputs))
    assert result.exit_code == 0
    assert "Position updated to -10.0 units" in result.output


def test_position_details_not_found():
    runner = CliRunner()
    result = runner.invoke(cli, ["position", "details", "-s", "GOOGL"])
    assert result.exit_code == 0
    assert "No position found for symbol='GOOGL'" in result.output


@mock.patch("inquirer.list_input")
def test_position_details_after_trade(mock_list_input):
    mock_list_input.side_effect = ["Total", "USD"]

    runner = CliRunner()
    inputs = ["MSFT", "10", "150"]
    runner = CliRunner()
    result = runner.invoke(cli, ["position", "sell"], input="\n".join(inputs))
    assert result.exit_code == 0
    assert "Position updated to -10.0 units" in result.output

    result = runner.invoke(cli, ["position", "details", "-s", "GOOGL"])
    assert result.exit_code == 0


@mock.patch("inquirer.list_input")
def test_position_provider_api_error(mock_list_input):
    mock_list_input.side_effect = ["Total", "USD"]

    runner = CliRunner()
    inputs = ["MSFT", "10", "150"]
    runner = CliRunner()
    result = runner.invoke(cli, ["position", "sell"], input="\n".join(inputs))
    assert result.exit_code == 0
    assert "Position updated to -10.0 units" in result.output

    Client.set_exception(ProviderAPIError(message="Fake Provider error"))
    result = runner.invoke(cli, ["position", "details", "-s", "GOOGL"])
    assert result.exit_code == 0
