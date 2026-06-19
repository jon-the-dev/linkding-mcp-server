"""Entry point for the LinkDing MCP server."""

import logging

from linkding_mcp_server.config import get_settings
from linkding_mcp_server.tools import create_mcp_server


def main() -> None:
    """Configure and run the LinkDing MCP server.

    Reads settings from environment variables, registers all tools,
    and starts the MCP server. Handles clean shutdown on KeyboardInterrupt.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    settings = get_settings()

    if settings.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    mcp = create_mcp_server(settings)

    logger.info("Starting LinkDing MCP Server")
    logger.info("LinkDing URL: %s", settings.linkding_url)
    logger.info("Debug mode: %s", settings.debug)

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error: %s", e)
        raise


if __name__ == "__main__":
    main()
