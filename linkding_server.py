#!/usr/bin/env python3
"""
LinkDing MCP Server - Legacy Entry Point

This file maintains backward compatibility with the original server.
The actual implementation is now in the linkding_mcp_server package.
"""

from linkding_mcp_server.server import main

if __name__ == "__main__":
    main()