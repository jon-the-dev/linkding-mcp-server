#!/usr/bin/env python3
"""
Test script for LinkDing MCP Server

This script demonstrates how to use the LinkDing MCP server programmatically.
"""

import asyncio
from fastmcp import Client

async def test_linkding_server():
    """Test the LinkDing MCP server functionality"""
    
    # Create a client that connects to our server
    client = Client("linkding_server.py")
    
    try:
        async with client:
            print("🔗 Testing LinkDing MCP Server")
            print("=" * 40)
            
            # Test 1: List available tools
            print("\n1. Listing available tools...")
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            # Test 2: List tags
            print("\n2. Testing list_tags...")
            result = await client.call_tool("list_tags", {"limit": 10})
            print("Tags result:", result.content[0].text[:200] + "..." if len(result.content[0].text) > 200 else result.content[0].text)
            
            # Test 3: Search bookmarks
            print("\n3. Testing search_bookmarks...")
            result = await client.call_tool("search_bookmarks", {"limit": 5})
            print("Search result:", result.content[0].text[:200] + "..." if len(result.content[0].text) > 200 else result.content[0].text)
            
            # Test 4: Check a URL (example)
            print("\n4. Testing check_url...")
            result = await client.call_tool("check_url", {"url": "https://github.com"})
            print("URL check result:", result.content[0].text[:200] + "..." if len(result.content[0].text) > 200 else result.content[0].text)
            
            print("\n✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\nMake sure:")
        print("1. Your LinkDing server is running")
        print("2. You have created a .env file with LINKDING_API_TOKEN")
        print("3. The LINKDING_URL is correct")

if __name__ == "__main__":
    asyncio.run(test_linkding_server())
