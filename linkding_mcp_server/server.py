#!/usr/bin/env python3
"""
LinkDing MCP Server - Main Entry Point

A Model Context Protocol server for interacting with LinkDing bookmark manager.
"""

import sys

import structlog

from linkding_mcp_server import __version__
from linkding_mcp_server.config import Settings
from linkding_mcp_server.tools import create_mcp_server


# Configure structured logging
def configure_logging(settings):
    """Configure structured logging based on settings"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set log level
    import logging

    log_level = getattr(logging, settings.log_level, logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level,
    )


def main():
    """Main entry point for the server"""
    try:
        # Load settings (constructed explicitly; no global singleton)
        settings = Settings()

        # Configure logging
        configure_logging(settings)
        logger = structlog.get_logger()

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
