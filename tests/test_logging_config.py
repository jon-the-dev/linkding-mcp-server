"""Tests for reusable logging configuration."""

import logging
import sys
from unittest.mock import patch

import structlog

from linkding_mcp_server.config import Settings
from linkding_mcp_server.logging_config import configure_logging


def _settings(*, debug: bool, log_level: str) -> Settings:
    return Settings(
        linkding_api_token="token",
        debug=debug,
        log_level=log_level,
    )


def test_configure_logging_uses_json_renderer_by_default():
    """Production-style logging emits structured JSON at the configured level."""
    with (
        patch("linkding_mcp_server.logging_config.structlog.configure") as configure,
        patch("linkding_mcp_server.logging_config.logging.basicConfig") as basic_config,
    ):
        configure_logging(_settings(debug=False, log_level="WARNING"))

    processors = configure.call_args.kwargs["processors"]
    assert isinstance(processors[-1], structlog.processors.JSONRenderer)
    basic_config.assert_called_once_with(
        format="%(message)s",
        stream=sys.stderr,
        level=logging.WARNING,
    )


def test_configure_logging_uses_console_renderer_for_debug():
    """Debug mode selects the human-readable console renderer."""
    with (
        patch("linkding_mcp_server.logging_config.structlog.configure") as configure,
        patch("linkding_mcp_server.logging_config.logging.basicConfig"),
    ):
        configure_logging(_settings(debug=True, log_level="DEBUG"))

    processors = configure.call_args.kwargs["processors"]
    assert isinstance(processors[-1], structlog.dev.ConsoleRenderer)
