"""Tests for setup script"""

from unittest.mock import patch

import pytest

from linkding_mcp_server.setup import setup_environment


class TestSetupEnvironment:
    """Tests for setup_environment token handling"""

    @pytest.fixture
    def mock_env_file(self, tmp_path):
        """Provide a temp config path"""
        config_dir = tmp_path / ".linkding-mcp"
        config_file = config_dir / "config.env"
        return config_file

    @patch("linkding_mcp_server.setup.Path.home")
    def test_token_uses_getpass(self, mock_home, tmp_path):
        """Token input uses getpass (hidden input)"""
        mock_home.return_value = tmp_path
        with (
            patch(
                "linkding_mcp_server.setup.getpass.getpass",
                side_effect=["my-secret-token", "my-secret-token"],
            ) as mock_getpass,
            patch(
                "builtins.input",
                side_effect=[
                    "http://localhost:9090",
                    "n",
                    "n",
                ],
            ),
        ):
            result = setup_environment()

        assert result is True
        assert mock_getpass.call_count == 2
        config = (
            tmp_path / ".linkding-mcp" / "config.env"
        ).read_text()
        assert "my-secret-token" in config

    @patch("linkding_mcp_server.setup.Path.home")
    def test_token_mismatch_fails(self, mock_home, tmp_path):
        """Mismatched token confirmation returns False"""
        mock_home.return_value = tmp_path
        with (
            patch(
                "linkding_mcp_server.setup.getpass.getpass",
                side_effect=["token-one", "token-two"],
            ),
            patch(
                "builtins.input",
                return_value="http://localhost:9090",
            ),
        ):
            result = setup_environment()

        assert result is False

    @patch("linkding_mcp_server.setup.Path.home")
    def test_empty_token_fails(self, mock_home, tmp_path):
        """Empty token returns False"""
        mock_home.return_value = tmp_path
        with (
            patch(
                "linkding_mcp_server.setup.getpass.getpass",
                return_value="",
            ),
            patch(
                "builtins.input",
                return_value="http://localhost:9090",
            ),
        ):
            result = setup_environment()

        assert result is False
