"""Tests for linkding_mcp_server.tools.create_mcp_server and tool registration."""

from contextlib import asynccontextmanager

import pytest
from fastmcp import Client

from linkding_mcp_server import tools
from linkding_mcp_server.config import Settings
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


@pytest.fixture
def settings():
    """Settings injected explicitly into create_mcp_server (no global singleton)."""
    return Settings(linkding_api_token="test_token_12345", enable_destructive_actions=False)


def _patch_client(monkeypatch, fake):
    """Patch LinkDingClient in the tools module to yield the given fake client."""

    @asynccontextmanager
    async def _factory(_settings):
        yield fake

    monkeypatch.setattr(tools, "LinkDingClient", lambda settings: _factory(settings))


@pytest.mark.asyncio
async def test_all_tools_registered(settings):
    mcp = create_mcp_server(settings)
    async with Client(mcp) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert EXPECTED_TOOLS.issubset(names)


@pytest.mark.asyncio
async def test_destructive_action_blocked_by_default(settings):
    mcp = create_mcp_server(settings)
    async with Client(mcp) as client:
        result = await client.call_tool("add_bookmark", {"url": "https://example.com"})
    assert "Destructive actions are disabled" in result.content[0].text


@pytest.mark.asyncio
async def test_list_tags_happy_path(monkeypatch, settings):
    class FakeClient:
        async def get_tags(self, limit, offset):
            return TagList(
                count=1,
                next=None,
                previous=None,
                results=[Tag(id=1, name="python", date_added="2024-01-01T00:00:00Z")],
            )

    _patch_client(monkeypatch, FakeClient())
    mcp = create_mcp_server(settings)
    async with Client(mcp) as client:
        result = await client.call_tool("list_tags", {"limit": 10})
    assert '"name": "python"' in result.content[0].text


@pytest.mark.asyncio
async def test_list_tags_validates_limit(settings):
    mcp = create_mcp_server(settings)
    async with Client(mcp) as client:
        result = await client.call_tool("list_tags", {"limit": 0})
    assert "limit must be between 1 and 1000" in result.content[0].text
