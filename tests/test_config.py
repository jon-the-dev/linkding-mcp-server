"""Tests for configuration management"""

import pytest
from pydantic import ValidationError

from linkding_mcp_server.config import Settings, get_settings, reset_settings


@pytest.fixture(autouse=True)
def reset_settings_singleton():
    """Reset settings singleton before and after each test"""
    reset_settings()
    yield
    reset_settings()


class TestSettings:
    """Tests for Settings configuration"""

    def test_default_settings(self):
        """Test default settings values"""
        settings = Settings(linkding_api_token="test_token")
        assert str(settings.linkding_url) == "http://127.0.0.1:9090/"
        assert settings.enable_destructive_actions is False
        assert settings.request_timeout == 30
        assert settings.max_retries == 3
        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_api_token_validation(self):
        """Test that API token is validated"""
        # Valid token
        settings = Settings(linkding_api_token="valid_token_123")
        assert settings.linkding_api_token == "valid_token_123"

        # Invalid tokens
        with pytest.raises(ValidationError) as exc_info:
            Settings(linkding_api_token="")
        assert "Valid LinkDing API token is required" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Settings(linkding_api_token="your_api_token_here")
        assert "Valid LinkDing API token is required" in str(exc_info.value)

    def test_url_validation(self):
        """Test URL validation"""
        # Valid URLs
        settings = Settings(
            linkding_url="https://linkding.example.com",
            linkding_api_token="token"
        )
        assert str(settings.linkding_url) == "https://linkding.example.com/"

        settings = Settings(
            linkding_url="http://localhost:8080",
            linkding_api_token="token"
        )
        assert str(settings.linkding_url) == "http://localhost:8080/"

        # Invalid URL
        with pytest.raises(ValidationError):
            Settings(
                linkding_url="not-a-url",
                linkding_api_token="token"
            )

    def test_masked_token(self):
        """Test token masking for logs"""
        # Normal token
        settings = Settings(linkding_api_token="abcd1234efgh5678")
        masked = settings.get_masked_token()
        assert masked == "abcd...5678"

        # Short token
        settings = Settings(linkding_api_token="short")
        masked = settings.get_masked_token()
        assert masked == "***"

    def test_log_level_validation(self):
        """Test log level validation"""
        # Valid levels
        settings = Settings(linkding_api_token="token", log_level="DEBUG")
        assert settings.log_level == "DEBUG"

        settings = Settings(linkding_api_token="token", log_level="error")  # Case insensitive
        assert settings.log_level == "ERROR"

        # Invalid level
        with pytest.raises(ValidationError) as exc_info:
            Settings(linkding_api_token="token", log_level="INVALID")
        assert "Log level must be one of" in str(exc_info.value)

    def test_numeric_field_validation(self):
        """Test numeric field bounds validation"""
        # Valid values
        settings = Settings(
            linkding_api_token="token",
            request_timeout=60,
            max_retries=5,
            max_connections=500,
            rate_limit_calls=1000
        )
        assert settings.request_timeout == 60
        assert settings.max_retries == 5

        # Invalid values - timeout too high
        with pytest.raises(ValidationError):
            Settings(
                linkding_api_token="token",
                request_timeout=301  # Max is 300
            )

        # Invalid values - negative retries
        with pytest.raises(ValidationError):
            Settings(
                linkding_api_token="token",
                max_retries=-1
            )

        # Invalid values - too many connections
        with pytest.raises(ValidationError):
            Settings(
                linkding_api_token="token",
                max_connections=1001  # Max is 1000
            )

    def test_environment_variables(self, monkeypatch):
        """Test loading from environment variables"""
        # Set environment variables with LINKDING_ prefix
        monkeypatch.setenv("LINKDING_URL", "https://my-linkding.com")
        monkeypatch.setenv("LINKDING_API_TOKEN", "env_token_123")
        monkeypatch.setenv("LINKDING_DEBUG", "true")
        monkeypatch.setenv("LINKDING_ENABLE_DESTRUCTIVE_ACTIONS", "true")
        monkeypatch.setenv("LINKDING_REQUEST_TIMEOUT", "60")

        settings = Settings()
        assert str(settings.linkding_url) == "https://my-linkding.com/"
        assert settings.linkding_api_token == "env_token_123"
        assert settings.debug is True
        assert settings.enable_destructive_actions is True
        assert settings.request_timeout == 60

    def test_env_file_loading(self, tmp_path, monkeypatch):
        """Test loading from .env file"""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
LINKDING_URL=https://env-file.com
LINKDING_API_TOKEN=file_token_456
LINKDING_DEBUG=false
LINKDING_LOG_LEVEL=WARNING
""")

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        settings = Settings()
        assert str(settings.linkding_url) == "https://env-file.com/"
        assert settings.linkding_api_token == "file_token_456"
        assert settings.debug is False
        assert settings.log_level == "WARNING"

    def test_case_insensitive_env_vars(self, monkeypatch):
        """Test that environment variables work with LINKDING_ prefix"""
        # pydantic-settings v2 uses the prefix defined in model_config
        monkeypatch.setenv("LINKDING_URL", "https://uppercase.com")
        monkeypatch.setenv("LINKDING_API_TOKEN", "token")
        monkeypatch.setenv("LINKDING_DEBUG", "true")

        settings = Settings()
        assert str(settings.linkding_url) == "https://uppercase.com/"
        assert settings.debug is True

    def test_cache_settings(self):
        """Test cache TTL settings"""
        settings = Settings(
            linkding_api_token="token",
            cache_ttl=600
        )
        assert settings.cache_ttl == 600

        # Test bounds
        with pytest.raises(ValidationError):
            Settings(
                linkding_api_token="token",
                cache_ttl=-1  # Must be >= 0
            )

        with pytest.raises(ValidationError):
            Settings(
                linkding_api_token="token",
                cache_ttl=3601  # Max is 3600
            )

    def test_rate_limit_settings(self):
        """Test rate limiting settings"""
        settings = Settings(
            linkding_api_token="token",
            rate_limit_calls=200,
            rate_limit_period=120
        )
        assert settings.rate_limit_calls == 200
        assert settings.rate_limit_period == 120

        # Test bounds
        with pytest.raises(ValidationError):
            Settings(
                linkding_api_token="token",
                rate_limit_calls=0  # Must be >= 1
            )

        with pytest.raises(ValidationError):
            Settings(
                linkding_api_token="token",
                rate_limit_period=3601  # Max is 3600
            )

    def test_ssl_defaults(self):
        """Test that SSL settings have correct defaults."""
        settings = Settings(linkding_api_token="token")
        assert settings.verify_ssl is True
        assert settings.ssl_cert_path is None

    def test_ssl_disabled(self):
        """Test disabling SSL verification."""
        settings = Settings(linkding_api_token="token", verify_ssl=False)
        assert settings.verify_ssl is False

    def test_ssl_cert_path_invalid(self):
        """Test that a non-existent cert path raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(linkding_api_token="token", ssl_cert_path="/nonexistent/path/ca-bundle.crt")
        assert "SSL certificate file not found" in str(exc_info.value)

    def test_ssl_cert_path_valid(self, tmp_path):
        """Test that a valid cert path is accepted."""
        cert_file = tmp_path / "ca-bundle.crt"
        cert_file.write_text("fake cert content")

        settings = Settings(linkding_api_token="token", ssl_cert_path=str(cert_file))
        assert settings.ssl_cert_path == str(cert_file)


class TestSSLEnvVars:
    """Tests for SSL/TLS environment variable parsing."""

    def test_verify_ssl_false_from_env(self, monkeypatch):
        """LINKDING_VERIFY_SSL=false disables SSL verification."""
        monkeypatch.setenv("LINKDING_API_TOKEN", "token")
        monkeypatch.setenv("LINKDING_VERIFY_SSL", "false")

        settings = Settings()
        assert settings.verify_ssl is False

    def test_verify_ssl_true_by_default(self, monkeypatch):
        """LINKDING_VERIFY_SSL defaults to True when not set."""
        monkeypatch.setenv("LINKDING_API_TOKEN", "token")
        monkeypatch.delenv("LINKDING_VERIFY_SSL", raising=False)

        settings = Settings()
        assert settings.verify_ssl is True

    def test_verify_ssl_explicit_true_from_env(self, monkeypatch):
        """LINKDING_VERIFY_SSL=true keeps SSL verification enabled."""
        monkeypatch.setenv("LINKDING_API_TOKEN", "token")
        monkeypatch.setenv("LINKDING_VERIFY_SSL", "true")

        settings = Settings()
        assert settings.verify_ssl is True

    def test_ssl_cert_path_from_env(self, monkeypatch, tmp_path):
        """LINKDING_SSL_CERT_PATH sets the custom CA bundle path."""
        cert_file = tmp_path / "ca.pem"
        cert_file.write_text("fake ca content")

        monkeypatch.setenv("LINKDING_API_TOKEN", "token")
        monkeypatch.setenv("LINKDING_SSL_CERT_PATH", str(cert_file))

        settings = Settings()
        assert settings.ssl_cert_path == str(cert_file)

    def test_ssl_cert_path_empty_env_is_none(self, monkeypatch):
        """LINKDING_SSL_CERT_PATH unset means ssl_cert_path is None."""
        monkeypatch.setenv("LINKDING_API_TOKEN", "token")
        monkeypatch.delenv("LINKDING_SSL_CERT_PATH", raising=False)

        settings = Settings()
        assert settings.ssl_cert_path is None


class TestGetSettings:
    """Tests for get_settings singleton"""

    def test_singleton_pattern(self, monkeypatch):
        """Test that get_settings returns the same instance"""
        monkeypatch.setenv("LINKDING_API_TOKEN", "singleton_token")

        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_settings_initialization(self, monkeypatch):
        """Test settings initialization from environment"""
        monkeypatch.setenv("LINKDING_API_TOKEN", "singleton_token")
        settings = get_settings()
        assert settings.linkding_api_token == "singleton_token"
