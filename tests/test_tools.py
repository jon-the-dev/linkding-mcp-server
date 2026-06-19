"""Tests for linkding_mcp_server.tools.create_mcp_server."""

import httpx
import pytest
import respx
from fastmcp import Client

from linkding_mcp_server.config import Settings
from linkding_mcp_server.tools import create_mcp_server

BASE = "http://test.local/api"

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


def _settings(destructive: bool = False) -> Settings:
    return Settings(
        linkding_url="http://test.local",
        api_token="tok",
        enable_destructive_actions=destructive,
    )


@pytest.mark.asyncio
async def test_all_tools_registered():
    mcp = create_mcp_server(_settings())
    async with Client(mcp) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert EXPECTED_TOOLS.issubset(names)


@pytest.mark.asyncio
async def test_destructive_action_blocked_by_default():
    mcp = create_mcp_server(_settings(destructive=False))
    async with Client(mcp) as client:
        result = await client.call_tool("add_bookmark", {"url": "https://example.com"})
    assert "Destructive actions are disabled" in result.content[0].text


@pytest.mark.asyncio
@respx.mock
async def test_list_tags_happy_path():
    respx.get(f"{BASE}/tags/").mock(
        return_value=httpx.Response(
            200,
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{"id": 1, "name": "python", "date_added": "2024-01-01"}],
            },
        )
    )
    mcp = create_mcp_server(_settings())
    async with Client(mcp) as client:
        result = await client.call_tool("list_tags", {"limit": 10})
    assert '"name": "python"' in result.content[0].text


@pytest.mark.asyncio
@respx.mock
async def test_search_bookmarks_api_error_surfaced():
    respx.get(f"{BASE}/bookmarks/").mock(
        return_value=httpx.Response(403, json={"detail": "forbidden"})
    )
    mcp = create_mcp_server(_settings())
    async with Client(mcp) as client:
        result = await client.call_tool("search_bookmarks", {"query": "x"})
    assert "API Error: forbidden" in result.content[0].text
