#!/usr/bin/env python3
"""Manual integration test script for the LinkDing MCP Server.

Requires a live LinkDing instance and LINKDING_API_TOKEN set in the environment
(or a .env file). Run directly: python tests/manual_integration.py
"""

import asyncio

from fastmcp import Client

from linkding_mcp_server.config import Settings
from linkding_mcp_server.tools import create_mcp_server


async def test_linkding_server():
    """Test the LinkDing MCP server against a live LinkDing instance."""
    settings = Settings.from_env()
    mcp = create_mcp_server(settings)

    async with Client(mcp) as client:
        print("Testing LinkDing MCP Server")
        print("=" * 40)

        print("\n1. Listing available tools...")
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")

        print("\n2. Testing list_tags...")
        result = await client.call_tool("list_tags", {"limit": 10})
        text = result.content[0].text
        print("Tags result:", text[:200] + "..." if len(text) > 200 else text)

        print("\n3. Testing search_bookmarks...")
        result = await client.call_tool("search_bookmarks", {"limit": 5})
        text = result.content[0].text
        print("Search result:", text[:200] + "..." if len(text) > 200 else text)

        print("\n4. Testing check_url...")
        result = await client.call_tool("check_url", {"url": "https://github.com"})
        text = result.content[0].text
        print("URL check result:", text[:200] + "..." if len(text) > 200 else text)

        print("\nAll tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_linkding_server())
