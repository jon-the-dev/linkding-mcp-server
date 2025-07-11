# Claude Desktop Integration

Integrate the LinkDing MCP Server with Claude Desktop to manage your bookmarks directly through conversations with Claude.

## Overview

Claude Desktop supports the Model Context Protocol (MCP), allowing you to extend Claude's capabilities with custom tools. The LinkDing MCP Server provides Claude with the ability to:

- Search your bookmarks during conversations
- Add new bookmarks you discover while chatting
- Update and organize your bookmark collection
- Check for duplicate URLs before bookmarking
- Manage tags and archive bookmarks

## Prerequisites

- Claude Desktop application installed
- LinkDing MCP Server set up and working
- LinkDing instance running and accessible

## Configuration

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
      "command": "python",
      "args": ["/absolute/path/to/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

!!! important "Use Absolute Paths"
    Always use absolute paths in the configuration. Relative paths may not work correctly.

### Step 3: Configuration Examples

#### Local LinkDing Instance
```json
{
  "mcpServers": {
    "linkding": {
      "command": "python",
      "args": ["/Users/username/code/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "abcd1234efgh5678ijkl9012mnop3456"
      }
    }
  }
}
```

#### Remote LinkDing Instance
```json
{
  "mcpServers": {
    "linkding": {
      "command": "python",
      "args": ["/home/user/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "https://bookmarks.example.com",
        "LINKDING_API_TOKEN": "your_secure_token_here"
      }
    }
  }
}
```

#### Using Virtual Environment
```json
{
  "mcpServers": {
    "linkding": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop completely:

1. **Quit Claude Desktop** (not just close the window)
2. **Relaunch Claude Desktop**
3. **Wait for initialization** (may take a few seconds)

## Verification

### Check Server Connection

Start a new conversation with Claude and ask:

```
Can you list my available MCP tools?
```

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

Try these test commands:

```
Can you search my bookmarks for "python"?
```

```
Can you list all my bookmark tags?
```

```
Can you check if https://python.org is already in my bookmarks?
```

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

## Advanced Configuration

### Multiple LinkDing Instances

You can configure multiple LinkDing instances:

```json
{
  "mcpServers": {
    "linkding-personal": {
      "command": "python",
      "args": ["/path/to/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "personal_token"
      }
    },
    "linkding-work": {
      "command": "python",
      "args": ["/path/to/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "https://work-bookmarks.company.com",
        "LINKDING_API_TOKEN": "work_token"
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
      "command": "python",
      "args": ["/path/to/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_token",
        "DEBUG": "true"
      }
    }
  }
}
```

### Custom Python Path

If you need to use a specific Python installation:

```json
{
  "mcpServers": {
    "linkding": {
      "command": "/usr/local/bin/python3.12",
      "args": ["/path/to/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_token"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

#### "No MCP servers found"

**Cause:** Configuration file not found or malformed JSON

**Solution:**
1. Verify the configuration file path
2. Check JSON syntax with a validator
3. Ensure proper file permissions

#### "Server failed to start"

**Cause:** Python path or script path incorrect

**Solution:**
1. Use absolute paths for both `command` and `args`
2. Test the command manually in terminal
3. Check Python version compatibility (3.12+)

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
3. Restart Claude Desktop

### Debug Steps

#### 1. Test Server Manually

```bash
cd /path/to/linkding-mcp-server
python linkding_server.py
```

#### 2. Check Configuration Syntax

```bash
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### 3. Verify Environment Variables

```bash
export LINKDING_URL="http://127.0.0.1:9090"
export LINKDING_API_TOKEN="your_token"
python linkding_server.py
```

#### 4. Test API Connectivity

```bash
curl -H "Authorization: Token your_token" http://127.0.0.1:9090/api/bookmarks/
```

### Log Analysis

Enable debug mode and check Claude Desktop logs:

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/claude_desktop.log
```

**Windows:**
```bash
type %APPDATA%\Claude\Logs\claude_desktop.log
```

## Best Practices

### Security

- **Never commit API tokens** to version control
- **Use environment-specific tokens** for different setups
- **Rotate tokens regularly** for security
- **Limit token permissions** if supported by your LinkDing version

### Performance

- **Use reasonable limits** when searching (default 100 is usually fine)
- **Be specific in searches** to reduce response size
- **Use pagination** for large result sets
- **Cache frequently accessed data** when possible

### Organization

- **Establish consistent tagging** conventions before heavy usage
- **Use descriptive bookmark titles** for better search results
- **Regular maintenance** of tags and archived items
- **Backup your LinkDing data** regularly

## Integration Patterns

### Conversational Bookmarking

```
You: "I'm reading about Rust programming and found some great resources. Can you help me bookmark them with proper organization?"

Claude: "I'd be happy to help you bookmark Rust resources! First, let me check what Rust-related bookmarks you already have..."

[Claude uses search_bookmarks to find existing Rust content]

Claude: "I found you have 5 existing Rust bookmarks tagged with 'rust' and 'programming'. What new resources would you like to add?"

You: "Here are three articles: [URLs]"

Claude: [Uses check_url for each, then add_bookmark with consistent tagging]
```

### Research Session Management

```
You: "I'm starting research on GraphQL. Can you help me organize a research session?"

Claude: "I'll help you set up a GraphQL research session. Let me first check what GraphQL resources you already have..."

[Claude searches existing bookmarks, creates a research tag, and helps organize new findings]
```

### Content Discovery

```
You: "What are some good tutorials I've bookmarked that I haven't read yet?"

Claude: [Uses search_bookmarks with unread_only=True and tag filters to find relevant tutorials]
```

## Next Steps

- **[Other MCP Clients](clients.md)** - Use with other MCP-compatible applications
- **[API Reference](../api/reference.md)** - Technical implementation details
- **[Development Guide](../development/contributing.md)** - Contribute to the project