"""Offline tests for package, CLI, and server entry points."""

import runpy
from unittest.mock import MagicMock, patch

import pytest

import linkding_mcp_server
from linkding_mcp_server import cli, server
from linkding_mcp_server.config import Settings


def _settings():
    return Settings(linkding_api_token="token")


def test_lazy_package_exports():
    assert linkding_mcp_server.__getattr__("main") is server.main
    assert callable(linkding_mcp_server.__getattr__("create_mcp_server"))
    with pytest.raises(AttributeError):
        linkding_mcp_server.__getattr__("missing")


def test_server_main_runs_configured_mcp():
    mcp = MagicMock()
    logger = MagicMock()
    with (
        patch.object(server, "Settings", return_value=_settings()),
        patch.object(server, "configure_logging") as configure,
        patch.object(server, "create_mcp_server", return_value=mcp),
        patch.object(server.structlog, "get_logger", return_value=logger),
    ):
        server.main()

    configure.assert_called_once()
    mcp.run.assert_called_once_with()
    logger.info.assert_any_call("server_ready")


@pytest.mark.parametrize(
    ("failure", "exit_code", "event"),
    [
        (KeyboardInterrupt(), 0, "server_stopped"),
        (RuntimeError("boom"), 1, "server_error"),
    ],
)
def test_server_main_handles_shutdown_and_failure(failure, exit_code, event):
    mcp = MagicMock()
    mcp.run.side_effect = failure
    logger = MagicMock()
    with (
        patch.object(server, "Settings", return_value=_settings()),
        patch.object(server, "configure_logging"),
        patch.object(server, "create_mcp_server", return_value=mcp),
        patch.object(server.structlog, "get_logger", return_value=logger),
        pytest.raises(SystemExit) as raised,
    ):
        server.main()

    assert raised.value.code == exit_code
    getattr(logger, "info" if exit_code == 0 else "error").assert_called()
    assert getattr(logger, "info" if exit_code == 0 else "error").call_args.args[0] == event


def test_server_reports_settings_failure():
    logger = MagicMock()
    with (
        patch.object(server, "Settings", side_effect=RuntimeError("bad config")),
        patch.object(server.structlog, "get_logger", return_value=logger),
        pytest.raises(SystemExit) as raised,
    ):
        server.main()

    assert raised.value.code == 1
    logger.error.assert_called_once()


def test_cli_main_success():
    with patch.object(cli, "server_main") as server_main:
        cli.main()
    server_main.assert_called_once_with()


@pytest.mark.parametrize(
    ("failure", "exit_code"),
    [(KeyboardInterrupt(), 0), (RuntimeError("boom"), 1)],
)
def test_cli_main_handles_failures(failure, exit_code, capsys):
    with (
        patch.object(cli, "server_main", side_effect=failure),
        pytest.raises(SystemExit) as raised,
    ):
        cli.main()

    assert raised.value.code == exit_code
    if exit_code == 1:
        assert "Error: boom" in capsys.readouterr().err


def test_module_entrypoint_calls_cli_main():
    with patch.object(cli, "main") as main:
        runpy.run_module("linkding_mcp_server.__main__", run_name="__main__")
    main.assert_called_once_with()
