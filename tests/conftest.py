"""Shared pytest fixtures for the linkding_mcp_server test suite."""

import pytest

from linkding_mcp_server.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Return a Settings instance pre-configured for testing (no real server needed)."""
    return Settings(linkding_url="http://test.local", api_token="test-token")
