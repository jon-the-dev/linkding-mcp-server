"""Tests for server startup metadata."""

from linkding_mcp_server import __version__, server


def test_server_uses_package_version():
    """Server logging and package metadata share one version source."""
    assert server.__version__ == __version__
