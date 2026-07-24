"""Offline MCP-to-LinkDing API integration, concurrency, and load tests."""

import asyncio
import json
import time
from contextlib import asynccontextmanager

import httpx
import pytest
from fastmcp import Client

from linkding_mcp_server.client import LinkDingClient
from linkding_mcp_server.config import Settings
from linkding_mcp_server.tools import create_mcp_server


def _bookmark(bookmark_id: int = 1, *, tags: list[str] | None = None) -> dict:
    return {
        "id": bookmark_id,
        "url": f"https://example.com/{bookmark_id}",
        "title": f"Bookmark {bookmark_id}",
        "description": "",
        "notes": "",
        "is_archived": False,
        "unread": False,
        "shared": False,
        "tag_names": tags or ["python"],
        "date_added": "2024-01-01T00:00:00Z",
        "date_modified": "2024-01-01T00:00:00Z",
    }


class LinkDingRouter:
    """Stateful in-process LinkDing API boundary."""

    def __init__(self, *, error_status: int | None = None):
        self.requests: list[httpx.Request] = []
        self.error_status = error_status

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.error_status is not None:
            return httpx.Response(
                self.error_status,
                text="offline test failure",
                request=request,
            )

        path = request.url.path
        if path == "/api/tags/":
            return httpx.Response(
                200,
                json={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "python",
                            "date_added": "2024-01-01T00:00:00Z",
                        }
                    ],
                },
                request=request,
            )
        if path == "/api/bookmarks/check/":
            return httpx.Response(
                200,
                json={"bookmark": _bookmark(), "metadata": {}, "auto_tags": []},
                request=request,
            )
        if path in {"/api/bookmarks/", "/api/bookmarks/archived/"}:
            if request.method == "POST":
                return httpx.Response(201, json=_bookmark(), request=request)
            bookmark_id = int(request.url.params.get("offset", "0")) + 1
            return httpx.Response(
                200,
                json={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [_bookmark(bookmark_id)],
                },
                request=request,
            )
        if path == "/api/bookmarks/1/":
            if request.method == "DELETE":
                return httpx.Response(204, request=request)
            return httpx.Response(200, json=_bookmark(), request=request)
        if path in {
            "/api/bookmarks/1/archive/",
            "/api/bookmarks/1/unarchive/",
        }:
            return httpx.Response(204, request=request)
        return httpx.Response(404, json={"detail": "not found"}, request=request)


def _server(router: LinkDingRouter):
    settings = Settings(
        linkding_url="https://linkding.test",
        linkding_api_token="offline-token",
        enable_destructive_actions=True,
        cache_ttl=0,
        rate_limit_calls=10_000,
    )
    transport = httpx.MockTransport(router)

    @asynccontextmanager
    async def client_factory(runtime_settings):
        client = LinkDingClient(runtime_settings)
        client.client = httpx.AsyncClient(
            base_url="https://linkding.test/api",
            headers={"Authorization": "Token offline-token"},
            transport=transport,
        )
        try:
            yield client
        finally:
            await client.client.aclose()

    return create_mcp_server(settings, client_factory=client_factory)


def _text(result) -> str:
    return result.content[0].text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_all_tools_through_offline_http_boundary():
    """Exercise every MCP tool through the production HTTP client."""
    router = LinkDingRouter()
    async with Client(_server(router)) as client:
        results = {
            "search": await client.call_tool(
                "search_bookmarks",
                {"query": "python", "tag": "python", "unread_only": False},
            ),
            "add": await client.call_tool(
                "add_bookmark",
                {"url": "https://example.com", "title": "Example"},
            ),
            "get": await client.call_tool("get_bookmark", {"bookmark_id": 1}),
            "update": await client.call_tool(
                "update_bookmark",
                {"bookmark_id": 1, "title": "Updated", "shared": False},
            ),
            "delete": await client.call_tool("delete_bookmark", {"bookmark_id": 1}),
            "archive": await client.call_tool("archive_bookmark", {"bookmark_id": 1}),
            "unarchive": await client.call_tool(
                "unarchive_bookmark",
                {"bookmark_id": 1},
            ),
            "check": await client.call_tool(
                "check_url",
                {"url": "https://example.com"},
            ),
            "tags": await client.call_tool("list_tags", {"limit": 10}),
            "by_tag": await client.call_tool(
                "list_bookmarks_by_tag",
                {"tag_name": "python"},
            ),
        }

    assert '"title": "Bookmark 1"' in _text(results["search"])
    assert '"id": 1' in _text(results["add"])
    assert '"id": 1' in _text(results["get"])
    assert '"id": 1' in _text(results["update"])
    assert _text(results["delete"]) == "Bookmark 1 deleted successfully"
    assert _text(results["archive"]) == "Bookmark 1 archived successfully"
    assert _text(results["unarchive"]) == "Bookmark 1 unarchived successfully"
    assert '"bookmark"' in _text(results["check"])
    assert '"name": "python"' in _text(results["tags"])
    assert '"tag_names": [' in _text(results["by_tag"])

    calls = {(request.method, request.url.path) for request in router.requests}
    assert ("POST", "/api/bookmarks/") in calls
    assert ("PATCH", "/api/bookmarks/1/") in calls
    assert ("DELETE", "/api/bookmarks/1/") in calls
    assert all(
        request.headers["Authorization"] == "Token offline-token"
        for request in router.requests
    )


ERROR_TOOL_CALLS = [
    ("search_bookmarks", {}),
    ("add_bookmark", {"url": "https://example.com"}),
    ("get_bookmark", {"bookmark_id": 1}),
    ("update_bookmark", {"bookmark_id": 1, "title": "Updated"}),
    ("delete_bookmark", {"bookmark_id": 1}),
    ("archive_bookmark", {"bookmark_id": 1}),
    ("unarchive_bookmark", {"bookmark_id": 1}),
    ("check_url", {"url": "https://example.com"}),
    ("list_tags", {}),
    ("list_bookmarks_by_tag", {"tag_name": "python"}),
]


@pytest.mark.integration
@pytest.mark.parametrize(("tool_name", "arguments"), ERROR_TOOL_CALLS)
@pytest.mark.asyncio
async def test_every_tool_translates_api_failures(tool_name, arguments):
    """All MCP operations produce stable values for upstream 500 responses."""
    async with Client(_server(LinkDingRouter(error_status=500))) as client:
        result = await client.call_tool(tool_name, arguments)

    assert _text(result).startswith("Error:")
    assert "offline-token" not in _text(result)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fifty_concurrent_operations_remain_isolated():
    """Concurrent requests retain their own offsets and results."""
    router = LinkDingRouter()
    async with Client(_server(router)) as client:
        results = await asyncio.gather(
            *[
                client.call_tool("search_bookmarks", {"offset": index})
                for index in range(50)
            ]
        )

    returned_ids = {
        json.loads(_text(result))["results"][0]["id"] for result in results
    }
    assert returned_ids == set(range(1, 51))
    assert len(router.requests) == 50


@pytest.mark.performance
@pytest.mark.asyncio
async def test_offline_mcp_load_baseline():
    """Provide a generous deterministic baseline for 100 in-process calls."""
    router = LinkDingRouter()
    started_at = time.perf_counter()
    async with Client(_server(router)) as client:
        await asyncio.gather(
            *[client.call_tool("get_bookmark", {"bookmark_id": 1}) for _ in range(100)]
        )
    elapsed = time.perf_counter() - started_at

    assert len(router.requests) == 100
    assert elapsed < 10
