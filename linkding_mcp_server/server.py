#!/usr/bin/env python3
"""
LinkDing MCP Server - Main Entry Point

A Model Context Protocol server for interacting with LinkDing bookmark manager.
"""

import sys

import structlog

from linkding_mcp_server import __version__
from linkding_mcp_server.config import Settings
from linkding_mcp_server.logging_config import configure_logging
from linkding_mcp_server.tools import create_mcp_server


def main():
    """Main entry point for the server"""
    logger = structlog.get_logger()
    try:
        # Load settings (constructed explicitly; no global singleton)
        settings = Settings()

        # Configure logging
        configure_logging(settings)

        logger.info(
            "server_starting",
            name="LinkDing MCP Server",
            version=__version__,
            linkding_url=str(settings.linkding_url),
            masked_token=settings.get_masked_token(),
            debug_mode=settings.debug,
            destructive_actions=settings.enable_destructive_actions,
        )

        # Create MCP server with explicitly injected settings
        mcp = create_mcp_server(settings)

        # Run the server
        logger.info("server_ready")
        mcp.run()

    except KeyboardInterrupt:
        logger.info("server_stopped", reason="user_interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error("server_error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
