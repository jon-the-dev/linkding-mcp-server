"""Tests for linkding_mcp_server.tools.create_mcp_server and tool registration."""

from contextlib import asynccontextmanager

import pytest
from fastmcp import Client

from linkding_mcp_server import tools
from linkding_mcp_server.config import reset_settings
from linkding_mcp_server.models import Tag, TagList
from linkding_mcp_server.tools import create_mcp_server

EXPECTED_TOOLS = {
    "search_bookmarks",
    "add_bookmark",
    "get_bookmark",
    "update_bookmark",
    "delete_bookmark",
    "archive_bookmark",
    "unarchive_bookmark",
    "check_url",
    "list_tags",
    "list_bookmarks_by_tag",
}


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    """Provide a valid token so get_settings() succeeds, and reset the singleton."""
    monkeypatch.setenv("LINKDING_API_TOKEN", "test_token_12345")
    monkeypatch.delenv("LINKDING_ENABLE_DESTRUCTIVE_ACTIONS", raising=False)
    reset_settings()
    yield
    reset_settings()


def _patch_client(monkeypatch, fake):
    """Patch LinkDingClient in the tools module to yield the given fake client."""

    @asynccontextmanager
    async def _factory(_settings):
        yield fake

    monkeypatch.setattr(tools, "LinkDingClient", lambda settings: _factory(settings))


@pytest.mark.asyncio
async def test_all_tools_registered():
    mcp = create_mcp_server()
    async with Client(mcp) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert EXPECTED_TOOLS.issubset(names)


@pytest.mark.asyncio
async def test_destructive_action_blocked_by_default():
    mcp = create_mcp_server()
    async with Client(mcp) as client:
        result = await client.call_tool("add_bookmark", {"url": "https://example.com"})
    assert "Destructive actions are disabled" in result.content[0].text


@pytest.mark.asyncio
async def test_list_tags_happy_path(monkeypatch):
    class FakeClient:
        async def get_tags(self, limit, offset):
            return TagList(
                count=1,
                next=None,
                previous=None,
                results=[Tag(id=1, name="python", date_added="2024-01-01T00:00:00Z")],
            )

    _patch_client(monkeypatch, FakeClient())
    mcp = create_mcp_server()
    async with Client(mcp) as client:
        result = await client.call_tool("list_tags", {"limit": 10})
    assert '"name": "python"' in result.content[0].text


@pytest.mark.asyncio
async def test_list_tags_validates_limit():
    mcp = create_mcp_server()
    async with Client(mcp) as client:
        result = await client.call_tool("list_tags", {"limit": 0})
    assert "limit must be between 1 and 1000" in result.content[0].text
