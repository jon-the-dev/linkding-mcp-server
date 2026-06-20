# LinkDing MCP Server

A Model Context Protocol (MCP) server for interacting with [LinkDing](https://github.com/sissbruecker/linkding), the self-hosted bookmark manager. This server enables LLMs like Claude to search, add, update, and manage bookmarks through natural conversation.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. MCP enables communication between AI assistants and locally running MCP servers that provide additional tools and resources to extend LLM capabilities.

## Features

- **Search bookmarks** with flexible filtering (query, tags, archived status)
- **Add new bookmarks** with automatic metadata scraping
- **Update existing bookmarks** (title, description, notes, tags, etc.)
- **Delete bookmarks** by ID
- **Archive/unarchive bookmarks** for organization
- **Check URL status** to see if already bookmarked
- **List and filter by tags** for better organization
- **Retrieve bookmark details** by ID

## Quick Start

### 1. Install

```bash
pip install linkding-mcp-server
```

### 2. Configure

```bash
linkding-mcp-setup
```

### 3. Use with Claude

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "linkding": {
      "command": "linkding-mcp",
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

Then ask Claude things like:

> "Search my bookmarks for Python tutorials"

> "Save this URL to my bookmarks: https://example.com"

> "What tags do I have in my bookmarks?"

## Available Tools

The server provides 10 comprehensive tools for bookmark management:

| Tool | Description |
|------|-------------|
| `search_bookmarks` | Search bookmarks with filters |
| `add_bookmark` | Add new bookmarks |
| `get_bookmark` | Retrieve bookmark by ID |
| `update_bookmark` | Update existing bookmarks |
| `delete_bookmark` | Delete bookmarks |
| `archive_bookmark` | Archive bookmarks |
| `unarchive_bookmark` | Unarchive bookmarks |
| `check_url` | Check if URL is bookmarked |
| `list_tags` | List all available tags |
| `list_bookmarks_by_tag` | Filter bookmarks by specific tag |

## Prerequisites

- Python 3.12 or higher
- A running LinkDing instance (local or remote)
- LinkDing API token (available in LinkDing Settings)

## Key Capabilities

- **Security-First Design**: URL validation, token masking, SSL/TLS verification, optional write protection
- **Resilient Networking**: Automatic retry with exponential backoff
- **Performance Optimized**: Connection pooling, LRU caching with configurable size limits, rate limiting
- **Comprehensive Validation**: Input sanitization and type checking
- **Well-Tested**: Unit tests with high coverage
- **Structured Logging**: Debug-friendly with contextual information

## Next Steps

- [Installation Guide](installation.md) - Detailed setup instructions
- [Quick Start](quickstart.md) - Get running in 5 minutes
- [Example Prompts](examples/prompts.md) - Ways to use with Claude
- [Configuration](configuration.md) - Environment setup and options
- [Tools Reference](tools/overview.md) - Complete tool documentation
- [Claude Desktop Integration](integration/claude.md) - Use with Claude Desktop

## Support

- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions
- [GitHub Issues](https://github.com/jon-the-dev/linkding-mcp-server/issues) - Report bugs or request features
