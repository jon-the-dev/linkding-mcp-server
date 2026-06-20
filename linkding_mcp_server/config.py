"""Configuration management for LinkDing MCP Server"""

import logging
from pathlib import Path

from pydantic import AliasChoices, Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LINKDING_",
        case_sensitive=False,
        extra="ignore",
    )

    # LinkDing configuration - use validation_alias to support both prefixed and non-prefixed
    linkding_url: HttpUrl = Field(
        default="http://127.0.0.1:9090",
        validation_alias=AliasChoices("url", "linkding_url"),
        description="Base URL for LinkDing server",
    )
    linkding_api_token: str = Field(
        ...,
        validation_alias=AliasChoices("api_token", "linkding_api_token"),
        description="API token for LinkDing authentication",
    )

    # Security settings
    enable_destructive_actions: bool = Field(default=False, description="Enable write operations (add, update, delete)")
    verify_ssl: bool = Field(default=True, description="Enable SSL/TLS certificate verification")
    ssl_cert_path: str | None = Field(default=None, description="Path to custom CA bundle or certificate file")

    # Request configuration
    request_timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum number of retry attempts")

    # Connection pool settings
    max_connections: int = Field(default=100, ge=1, le=1000, description="Maximum number of connections")
    max_keepalive_connections: int = Field(
        default=20, ge=1, le=100, description="Maximum number of keepalive connections"
    )
    keepalive_expiry: float = Field(default=30.0, ge=1.0, le=300.0, description="Keepalive expiry in seconds")

    # Rate limiting
    rate_limit_calls: int = Field(default=100, ge=1, le=10000, description="Number of calls allowed per period")
    rate_limit_period: int = Field(default=60, ge=1, le=3600, description="Rate limit period in seconds")

    # Cache settings
    cache_ttl: int = Field(default=300, ge=0, le=3600, description="Cache TTL in seconds (0 to disable)")
    cache_max_size: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of items in cache",
    )

    # Debug settings
    debug: bool = Field(default=False, description="Enable debug logging")
    log_level: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")

    @field_validator("linkding_api_token")
    @classmethod
    def validate_api_token(cls, v):
        """Validate API token is not empty"""
        if not v or v == "your_api_token_here":
            raise ValueError("Valid LinkDing API token is required")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("ssl_cert_path")
    @classmethod
    def validate_ssl_cert_path(cls, v):
        """Validate SSL certificate path exists if provided."""
        if v is not None:
            cert_path = Path(v)
            if not cert_path.exists():
                raise ValueError(f"SSL certificate file not found: {v}")
        return v

    def get_masked_token(self) -> str:
        """Return masked version of API token for logging"""
        if not self.linkding_api_token:
            return "None"
        if len(self.linkding_api_token) < 8:
            return "***"
        return f"{self.linkding_api_token[:4]}...{self.linkding_api_token[-4:]}"

    def get_log_level_int(self) -> int:
        """Get log level as integer for tenacity compatibility"""
        return getattr(logging, self.log_level, logging.INFO)
