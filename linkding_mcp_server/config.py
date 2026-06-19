"""Settings and configuration for the LinkDing MCP server."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime configuration loaded from environment variables.

    Args:
        linkding_url: Base URL for the LinkDing instance.
        api_token: LinkDing API authentication token.
        debug: Enable debug logging when True.
        enable_destructive_actions: Allow write/delete operations when True.
    """

    linkding_url: str = "http://127.0.0.1:9090"
    api_token: str
    debug: bool = False
    enable_destructive_actions: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        """Build Settings from environment variables.

        Reads LINKDING_URL, LINKDING_API_TOKEN, DEBUG, and
        LINKDING_ENABLE_DESTRUCTIVE_ACTIONS from the environment.

        Returns:
            A fully configured Settings instance.

        Raises:
            ValueError: If LINKDING_API_TOKEN is missing or empty.
        """
        load_dotenv()

        token = os.getenv("LINKDING_API_TOKEN", "").strip()
        if not token:
            raise ValueError("LINKDING_API_TOKEN environment variable is required")

        url = os.getenv("LINKDING_URL", "http://127.0.0.1:9090").rstrip("/")
        debug = os.getenv("DEBUG", "false").lower() == "true"
        destructive = (
            os.getenv("LINKDING_ENABLE_DESTRUCTIVE_ACTIONS", "false").lower() == "true"
        )

        return cls(
            linkding_url=url,
            api_token=token,
            debug=debug,
            enable_destructive_actions=destructive,
        )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Return the module-level Settings singleton, building it on first call.

    Returns:
        The shared Settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def reset_settings() -> None:
    """Clear the cached settings singleton (used in tests)."""
    global _settings
    _settings = None
