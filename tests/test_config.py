"""Tests for linkding_mcp_server.config."""

import pytest

from linkding_mcp_server import config
from linkding_mcp_server.config import Settings, get_settings, reset_settings


@pytest.fixture(autouse=True)
def _clear_singleton():
    """Ensure each test starts and ends with a clean settings singleton."""
    reset_settings()
    yield
    reset_settings()


def test_from_env_requires_token(monkeypatch):
    monkeypatch.delenv("LINKDING_API_TOKEN", raising=False)
    # Avoid picking the token up from a local .env file.
    monkeypatch.setattr(config, "load_dotenv", lambda *a, **k: None)
    with pytest.raises(ValueError, match="LINKDING_API_TOKEN"):
        Settings.from_env()


def test_from_env_strips_trailing_slash_and_reads_flags(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("LINKDING_API_TOKEN", "abc123")
    monkeypatch.setenv("LINKDING_URL", "https://links.example.com/")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LINKDING_ENABLE_DESTRUCTIVE_ACTIONS", "TRUE")

    settings = Settings.from_env()

    assert settings.api_token == "abc123"
    assert settings.linkding_url == "https://links.example.com"
    assert settings.debug is True
    assert settings.enable_destructive_actions is True


def test_from_env_defaults(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("LINKDING_API_TOKEN", "tok")
    monkeypatch.delenv("LINKDING_URL", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("LINKDING_ENABLE_DESTRUCTIVE_ACTIONS", raising=False)

    settings = Settings.from_env()

    assert settings.linkding_url == "http://127.0.0.1:9090"
    assert settings.debug is False
    assert settings.enable_destructive_actions is False


def test_get_settings_is_cached(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("LINKDING_API_TOKEN", "tok")

    first = get_settings()
    second = get_settings()

    assert first is second


def test_reset_settings_forces_rebuild(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("LINKDING_API_TOKEN", "tok")

    first = get_settings()
    reset_settings()
    second = get_settings()

    assert first is not second
