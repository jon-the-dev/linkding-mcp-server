"""Tests for linkding_mcp_server.client."""

import httpx
import pytest

from linkding_mcp_server.client import LinkDingClient, handle_api_error
from linkding_mcp_server.config import Settings


def _response(status_code: int, json_data=None, text: str = "") -> httpx.Response:
    request = httpx.Request("GET", "http://test.local/api/bookmarks/")
    if json_data is not None:
        return httpx.Response(status_code, json=json_data, request=request)
    return httpx.Response(status_code, text=text, request=request)


@pytest.mark.asyncio
async def test_handle_api_error_prefers_detail():
    resp = _response(400, {"detail": "bad request"})
    assert await handle_api_error(resp) == "API Error: bad request"


@pytest.mark.asyncio
async def test_handle_api_error_prefers_error_key():
    resp = _response(400, {"error": "nope"})
    assert await handle_api_error(resp) == "API Error: nope"


@pytest.mark.asyncio
async def test_handle_api_error_falls_back_to_status_and_text():
    resp = _response(500, text="boom")
    assert await handle_api_error(resp) == "HTTP 500: boom"


def test_client_builds_base_url_and_auth_header():
    client = LinkDingClient(Settings(linkding_url="http://test.local", api_token="tok"))
    assert str(client._http.base_url) == "http://test.local/api/"
    assert client._http.headers["Authorization"] == "Token tok"


@pytest.mark.asyncio
async def test_client_aclose_is_idempotent():
    client = LinkDingClient(Settings(linkding_url="http://test.local", api_token="tok"))
    await client.aclose()
    # Closing an already-closed client must not raise.
    await client.aclose()
