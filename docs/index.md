# LinkDing MCP Server

A Model Context Protocol (MCP) server for interacting with [LinkDing](https://github.com/sissbruecker/linkding), the self-hosted bookmark manager. This server enables LLMs to search, add, update, and manage bookmarks through LinkDing's REST API.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. MCP enables communication between the system and locally running MCP servers that provide additional tools and resources to extend LLM capabilities.

## Features

- **🔍 Search bookmarks** with flexible filtering (query, tags, archived status)
- **➕ Add new bookmarks** with automatic metadata scraping
- **✏️ Update existing bookmarks** (title, description, notes, tags, etc.)
- **🗑️ Delete bookmarks** by ID
- **📦 Archive/unarchive bookmarks** for organization
- **✅ Check URL status** to see if already bookmarked
- **🏷️ List and filter by tags** for better organization
- **📋 Retrieve bookmark details** by ID

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.sample .env
   # Edit .env with your LinkDing URL and API token
   ```

3. **Run the server**:
   ```bash
   python linkding_server.py
   ```

## Available Tools

The server provides 9 comprehensive tools for bookmark management:

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
| `list_bookmarks_by_tag` | Filter bookmarks by tag |

## Prerequisites

- Python 3.12 or higher
- A running LinkDing instance (local or remote)
- LinkDing API token (available in LinkDing Settings)

## Next Steps

- [Installation Guide](installation.md) - Detailed setup instructions
- [Configuration](configuration.md) - Environment setup and options
- [Tools Reference](tools/overview.md) - Complete tool documentation
- [Claude Desktop Integration](integration/claude.md) - Use with Claude Desktop

## Support

- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions
- [GitHub Issues](https://github.com/your-username/linkding-mcp-server/issues) - Report bugs or request features