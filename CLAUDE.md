# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Model Context Protocol (MCP) server for interacting with LinkDing, the self-hosted bookmark manager. Built with FastMCP framework, enabling LLMs to search, add, update, and manage bookmarks through LinkDing's REST API.

## Build & Development Commands

```bash
# Install dependencies
pip install -r requirements.txt          # Production
pip install -r requirements-dev.txt      # Development

# Run the server
python -m linkding_mcp_server            # Module execution
linkding-mcp                             # CLI command (after install)

# Testing
pytest tests/                            # Run all tests
pytest tests/test_models.py              # Run specific test file
pytest tests/ --cov=linkding_mcp_server  # With coverage

# Code quality
ruff check linkding_mcp_server/ tests/   # Linting
black linkding_mcp_server/ tests/        # Formatting
mypy linkding_mcp_server/                # Type checking

# Build & publish
make build                               # Build distribution
make publish-test                        # Publish to TestPyPI
make publish                             # Publish to PyPI
```

## Architecture

```
linkding_mcp_server/
├── server.py    # Entry point, logging config, mcp.run()
├── tools.py     # MCP tool definitions (search, add, update, delete, etc.)
├── client.py    # Async HTTP client with retry logic, rate limiting, caching
├── config.py    # Pydantic settings with env var validation
├── models.py    # Pydantic models for bookmarks, tags, search params
├── cli.py       # CLI entry point
└── setup.py     # Interactive setup wizard
```

**Data Flow**: MCP tools (tools.py) -> LinkDingClient (client.py) -> LinkDing REST API

**Key Patterns**:
- Tools use `async with LinkDingClient(settings)` context manager for HTTP operations
- All write operations check `settings.enable_destructive_actions` before executing
- Client implements automatic retry with tenacity (exponential backoff)
- Rate limiting via `RateLimiter` class in client.py
- Tag caching with configurable TTL

## Configuration

Environment variables (prefix `LINKDING_`):
- `LINKDING_URL` - LinkDing server URL (required)
- `LINKDING_API_TOKEN` - API token (required)
- `LINKDING_ENABLE_DESTRUCTIVE_ACTIONS` - Enable write ops (default: false)

Config loaded via pydantic-settings from `.env` file or environment.

## Testing

Tests use pytest-asyncio with `asyncio_mode = auto`. Test markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (skip with `-m "not slow"`)

Settings singleton can be reset between tests with `reset_settings()`.
