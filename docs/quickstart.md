# Quick Start

Get up and running with the LinkDing MCP Server in minutes.

## Prerequisites Check

Before starting, ensure you have:

- Python 3.12+ installed
- LinkDing instance running
- LinkDing API token ready

## 5-Minute Setup

### 1. Install the Package

```bash
pip install linkding-mcp-server
```

### 2. Run the Setup Wizard

```bash
linkding-mcp-setup
```

Follow the prompts to configure your LinkDing connection. The wizard will:

- Ask for your LinkDing URL (e.g., `http://127.0.0.1:9090`)
- Ask for your API token
- Optionally enable destructive actions (add/update/delete)
- Test the connection

!!! info "Security Feature"
    By default, the server operates in **read-only mode** for security. You can search and view bookmarks, but cannot add, update, or delete them. To enable full functionality, answer "yes" when asked about destructive actions during setup.

### 3. Start the Server

```bash
linkding-mcp
```

The server will start and be ready for MCP client connections.

## Integration with Claude Desktop

To use with Claude Desktop, add this to your configuration:

### macOS Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "linkding": {
      "command": "linkding-mcp",
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_api_token_here",
        "LINKDING_ENABLE_DESTRUCTIVE_ACTIONS": "true"
      }
    }
  }
}
```

### Windows Configuration

Edit `%APPDATA%/Claude/claude_desktop_config.json` with the same content.

After adding the configuration, restart Claude Desktop.

## Integration with Claude Code

Add to your Claude Code MCP settings (`~/.claude.json`):

```json
{
  "mcpServers": {
    "linkding": {
      "command": "linkding-mcp",
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_api_token_here",
        "LINKDING_ENABLE_DESTRUCTIVE_ACTIONS": "true"
      }
    }
  }
}
```

## Try It Out

Once integrated with Claude, try these example prompts:

### Search Your Bookmarks

> "Search my bookmarks for Python tutorials"

> "What bookmarks do I have tagged with 'react'?"

> "Find my unread bookmarks"

### Add New Bookmarks

> "Bookmark https://docs.python.org with tags python and documentation"

> "Save this article for later: https://example.com/great-article"

### Organize Bookmarks

> "List all my tags"

> "Archive the bookmark about old JavaScript frameworks"

> "What tutorials have I saved but not read yet?"

### Check for Duplicates

> "Is https://github.com already in my bookmarks?"

> "Check if I've already saved this URL: https://example.com"

## Available Tools

The server provides these tools for LLM interaction:

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

## Troubleshooting Quick Fixes

### Server Won't Start

```bash
# Check environment variables are set
echo $LINKDING_URL
echo $LINKDING_API_TOKEN

# Verify LinkDing is running
curl http://127.0.0.1:9090/api/bookmarks/ -H "Authorization: Token YOUR_TOKEN"

# Check Python version
python --version  # Should be 3.12+
```

### API Errors

```bash
# Enable debug mode
export LINKDING_LOG_LEVEL=DEBUG
linkding-mcp
```

### Connection Issues

```bash
# Test LinkDing connectivity
curl -I http://127.0.0.1:9090
```

## Next Steps

Now that you're up and running:

- **[Example Prompts](examples/prompts.md)** - More ways to use with Claude
- **[Tools Reference](tools/overview.md)** - Detailed tool documentation
- **[Configuration](configuration.md)** - All configuration options
- **[Claude Desktop Integration](integration/claude.md)** - Advanced setup

## Getting Help

- **Common Issues**: Check [Troubleshooting](troubleshooting.md)
- **Questions**: See our [FAQ](faq.md)
- **Bugs**: Report on [GitHub Issues](https://github.com/jon-the-dev/linkding-mcp-server/issues)
