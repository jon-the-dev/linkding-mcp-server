#!/usr/bin/env python3
"""
LinkDing MCP Server - Command Line Interface
"""

import sys

from linkding_mcp_server.server import main as server_main


def main():
    """Main CLI entry point for linkding-mcp command"""
    try:
        server_main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
