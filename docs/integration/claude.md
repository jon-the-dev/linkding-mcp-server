# Claude Integration

Integrate the LinkDing MCP Server with Claude Desktop or Claude Code to manage your bookmarks directly through conversations.

## Overview

Claude supports the Model Context Protocol (MCP), allowing you to extend its capabilities with custom tools. The LinkDing MCP Server provides Claude with the ability to:

- Search your bookmarks during conversations
- Add new bookmarks you discover while chatting
- Update and organize your bookmark collection
- Check for duplicate URLs before bookmarking
- Manage tags and archive bookmarks

## Prerequisites

- LinkDing MCP Server installed (`pip install linkding-mcp-server`)
- LinkDing instance running and accessible
- LinkDing API token

## Claude Desktop Configuration

### Step 1: Locate Configuration File

Find your Claude Desktop configuration file:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%/Claude/claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add Server Configuration

Edit the configuration file to include the LinkDing MCP Server:

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

!!! warning "Security Note"
    The `LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=true` setting allows Claude to add, update, delete, and archive your bookmarks. Only enable this if you trust Claude with full access to your bookmark collection. Without this setting, Claude can only search and read your bookmarks.

### Step 3: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop completely:

1. **Quit Claude Desktop** (not just close the window)
2. **Relaunch Claude Desktop**
3. **Wait for initialization** (may take a few seconds)

## Claude Code Configuration

### Step 1: Locate Configuration File

Claude Code uses `~/.claude.json` for MCP server configuration.

### Step 2: Add Server Configuration

Edit `~/.claude.json` to include the LinkDing MCP Server:

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

### Step 3: Restart Claude Code

Restart Claude Code or start a new session for the configuration to take effect.

## Configuration Examples

### Using uv (Recommended)

If you installed with uv:

```json
{
  "mcpServers": {
    "linkding": {
      "command": "uv",
      "args": ["run", "linkding-mcp"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### Remote LinkDing Instance

```json
{
  "mcpServers": {
    "linkding": {
      "command": "linkding-mcp",
      "env": {
        "LINKDING_URL": "https://bookmarks.example.com",
        "LINKDING_API_TOKEN": "your_secure_token_here",
        "LINKDING_ENABLE_DESTRUCTIVE_ACTIONS": "true"
      }
    }
  }
}
```

### Multiple LinkDing Instances

You can configure multiple LinkDing instances:

```json
{
  "mcpServers": {
    "linkding-personal": {
      "command": "linkding-mcp",
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "personal_token",
        "LINKDING_ENABLE_DESTRUCTIVE_ACTIONS": "true"
      }
    },
    "linkding-work": {
      "command": "linkding-mcp",
      "env": {
        "LINKDING_URL": "https://work-bookmarks.company.com",
        "LINKDING_API_TOKEN": "work_token",
        "LINKDING_ENABLE_DESTRUCTIVE_ACTIONS": "true"
      }
    }
  }
}
```

### Debug Configuration

Enable debug mode for troubleshooting:

```json
{
  "mcpServers": {
    "linkding": {
      "command": "linkding-mcp",
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_token",
        "LINKDING_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Verification

### Check Server Connection

Start a new conversation with Claude and ask:

> "Can you list my available MCP tools?"

You should see the LinkDing tools listed, including:

- `search_bookmarks`
- `add_bookmark`
- `get_bookmark`
- `update_bookmark`
- `delete_bookmark`
- `archive_bookmark`
- `unarchive_bookmark`
- `check_url`
- `list_tags`
- `list_bookmarks_by_tag`

### Test Basic Functionality

Try these test prompts:

> "Search my bookmarks for python"

> "List all my bookmark tags"

> "Check if https://python.org is already in my bookmarks"

## Usage Examples

### Research Assistant

**You:** "I'm researching machine learning frameworks. Can you search my bookmarks for anything related to ML or AI?"

**Claude:** *Uses `search_bookmarks` to find relevant content and presents organized results*

**You:** "Great! I found this new article about PyTorch. Can you add it to my bookmarks with appropriate tags?"

**Claude:** *Uses `check_url` to avoid duplicates, then `add_bookmark` with relevant tags*

### Content Organization

**You:** "I have too many unread bookmarks. Can you help me organize them?"

**Claude:** *Uses `search_bookmarks` with `unread_only=True` to find unread items, then helps categorize and tag them*

### Bookmark Discovery

**You:** "What tutorials do I have bookmarked about React?"

**Claude:** *Uses `list_bookmarks_by_tag` or `search_bookmarks` to find React tutorials and presents them in a useful format*

### Duplicate Prevention

**You:** "I want to bookmark this article about FastAPI best practices: https://example.com/fastapi-guide"

**Claude:** *Uses `check_url` first, then either informs you it's already bookmarked or adds it with appropriate metadata*

For more example prompts, see the [Example Prompts](../examples/prompts.md) page.

## Troubleshooting

### Common Issues

#### "No MCP servers found"

**Cause:** Configuration file not found or malformed JSON

**Solution:**

1. Verify the configuration file path
2. Check JSON syntax with a validator
3. Ensure proper file permissions

#### "Server failed to start"

**Cause:** Package not installed or command not found

**Solution:**

1. Verify installation: `pip show linkding-mcp-server`
2. Check that `linkding-mcp` is in your PATH
3. Try using full path or `python -m linkding_mcp_server`

#### "Connection refused" errors

**Cause:** LinkDing instance not accessible

**Solution:**

1. Verify LinkDing is running
2. Check the `LINKDING_URL` in configuration
3. Test API connectivity manually

#### "Unauthorized" errors

**Cause:** Invalid or expired API token

**Solution:**

1. Generate a new API token in LinkDing
2. Update the `LINKDING_API_TOKEN` in configuration
3. Restart Claude

### Debug Steps

#### 1. Test Server Manually

```bash
linkding-mcp
```

Or with environment variables:

```bash
LINKDING_URL="http://127.0.0.1:9090" \
LINKDING_API_TOKEN="your_token" \
linkding-mcp
```

#### 2. Check Configuration Syntax

```bash
python -m json.tool ~/.claude.json
```

#### 3. Test API Connectivity

```bash
curl -H "Authorization: Token your_token" http://127.0.0.1:9090/api/bookmarks/
```

### Log Analysis

Enable debug mode and check logs:

**Claude Desktop (macOS):**
```bash
tail -f ~/Library/Logs/Claude/claude_desktop.log
```

**Claude Desktop (Windows):**
```bash
type %APPDATA%\Claude\Logs\claude_desktop.log
```

## Best Practices

### Security

- **Never commit API tokens** to version control
- **Use environment-specific tokens** for different setups
- **Rotate tokens regularly** for security
- **Start with read-only mode** until you're comfortable

### Performance

- **Use reasonable limits** when searching (default 100 is usually fine)
- **Be specific in searches** to reduce response size
- **Use pagination** for large result sets

### Organization

- **Establish consistent tagging** conventions before heavy usage
- **Use descriptive bookmark titles** for better search results
- **Regular maintenance** of tags and archived items
- **Backup your LinkDing data** regularly

## Next Steps

- **[Example Prompts](../examples/prompts.md)** - More ways to use with Claude
- **[Other MCP Clients](clients.md)** - Use with other MCP-compatible applications
- **[Tools Reference](../tools/overview.md)** - Detailed tool documentation
