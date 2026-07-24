"""Contract tests for LinkDing client protocols."""

from contextlib import asynccontextmanager

import pytest
from fastmcp import Client

from linkding_mcp_server.client import LinkDingClient
from linkding_mcp_server.config import Settings
from linkding_mcp_server.models import Tag, TagList
from linkding_mcp_server.protocols import LinkDingClientProtocol
from linkding_mcp_server.tools import create_mcp_server


def test_linkding_client_satisfies_runtime_protocol():
    """The production client structurally implements the public contract."""
    settings = Settings(linkding_api_token="token")

    assert isinstance(LinkDingClient(settings), LinkDingClientProtocol)


@pytest.mark.asyncio
async def test_create_mcp_server_accepts_client_factory():
    """A protocol-compatible fake can be injected without global patching."""

    class FakeClient:
        async def get_tags(self, limit: int = 100, offset: int = 0) -> TagList:
            return TagList(
                count=1,
                next=None,
                previous=None,
                results=[
                    Tag(
                        id=1,
                        name="injected",
                        date_added="2024-01-01T00:00:00Z",
                    )
                ],
            )

    @asynccontextmanager
    async def client_factory(settings):
        yield FakeClient()

    settings = Settings(linkding_api_token="token")
    mcp = create_mcp_server(settings, client_factory=client_factory)

    async with Client(mcp) as client:
        result = await client.call_tool("list_tags", {})

    assert '"name": "injected"' in result.content[0].text
