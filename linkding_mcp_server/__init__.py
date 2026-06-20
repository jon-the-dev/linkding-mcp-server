"""LinkDing MCP Server Package"""

__version__ = "1.0.0"
__author__ = "Jon Price"
__email__ = "jon@jonprice.io"


def __getattr__(name):
    """Lazy imports to avoid loading settings at import time"""
    if name == "main":
        from linkding_mcp_server.server import main

        return main
    elif name == "create_mcp_server":
        from linkding_mcp_server.tools import create_mcp_server

        return create_mcp_server
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["main", "create_mcp_server", "__version__"]
