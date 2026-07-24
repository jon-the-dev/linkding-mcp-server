"""Offline tests for the interactive setup script."""

from unittest.mock import MagicMock, patch

import pytest

from linkding_mcp_server import setup
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

    @patch("linkding_mcp_server.setup.Path.home")
    def test_existing_configuration_is_preserved(self, mock_home, tmp_path):
        mock_home.return_value = tmp_path
        config_file = tmp_path / ".linkding-mcp" / "config.env"
        config_file.parent.mkdir()
        config_file.write_text("existing=true")

        with patch("builtins.input", return_value="n"):
            assert setup_environment() is True

        assert config_file.read_text() == "existing=true"

    @patch("linkding_mcp_server.setup.Path.home")
    def test_default_url_and_enabled_options_are_written(self, mock_home, tmp_path):
        mock_home.return_value = tmp_path
        with (
            patch(
                "linkding_mcp_server.setup.getpass.getpass",
                side_effect=["token", "token"],
            ),
            patch("builtins.input", side_effect=["", "yes", "y"]),
        ):
            assert setup_environment() is True

        config = (tmp_path / ".linkding-mcp" / "config.env").read_text()
        assert "LINKDING_URL=http://127.0.0.1:9090" in config
        assert "LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=true" in config
        assert "LINKDING_DEBUG=true" in config


def _http_client_with_status(status_code):
    client = MagicMock()
    client.__enter__.return_value.get.return_value.status_code = status_code
    return client


def test_check_python_version(capsys):
    assert setup.check_python_version() is True
    assert "Python version" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("status_code", "expected", "message"),
    [
        (200, True, "Successfully connected"),
        (401, False, "Authentication failed"),
        (503, False, "status 503"),
    ],
)
def test_connection_statuses(tmp_path, monkeypatch, capsys, status_code, expected, message):
    monkeypatch.setenv("LINKDING_API_TOKEN", "token")
    monkeypatch.setenv("LINKDING_URL", "https://linkding.test")
    client = _http_client_with_status(status_code)
    with (
        patch.object(setup.Path, "home", return_value=tmp_path),
        patch("httpx.Client", return_value=client),
    ):
        assert setup.test_connection() is expected

    assert message in capsys.readouterr().out


def test_connection_without_token(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("LINKDING_API_TOKEN", raising=False)
    with (
        patch.object(setup.Path, "home", return_value=tmp_path),
        patch("dotenv.load_dotenv"),
    ):
        assert setup.test_connection() is False
    assert "API token not found" in capsys.readouterr().out


def test_connection_handles_runtime_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LINKDING_API_TOKEN", "token")
    with (
        patch.object(setup.Path, "home", return_value=tmp_path),
        patch("httpx.Client", side_effect=RuntimeError("offline")),
    ):
        assert setup.test_connection() is False
    assert "offline" in capsys.readouterr().out


def test_setup_main_success(tmp_path, capsys):
    with (
        patch.object(setup, "check_python_version", return_value=True),
        patch.object(setup, "setup_environment", return_value=True),
        patch.object(setup, "test_connection") as test_connection,
        patch.object(setup.Path, "home", return_value=tmp_path),
    ):
        setup.main()

    test_connection.assert_called_once_with()
    assert "Setup completed" in capsys.readouterr().out


@pytest.mark.parametrize("failed_step", ["version", "environment"])
def test_setup_main_exits_when_required_step_fails(failed_step):
    with (
        patch.object(
            setup,
            "check_python_version",
            return_value=failed_step != "version",
        ),
        patch.object(
            setup,
            "setup_environment",
            return_value=failed_step != "environment",
        ),
        pytest.raises(SystemExit) as raised,
    ):
        setup.main()

    assert raised.value.code == 1
