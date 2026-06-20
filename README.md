# LinkDing MCP Server

[![PyPI version](https://badge.fury.io/py/linkding-mcp-server.svg)](https://badge.fury.io/py/linkding-mcp-server)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A Model Context Protocol (MCP) server for interacting with [LinkDing](https://github.com/sissbruecker/linkding), the self-hosted bookmark manager. This server enables LLMs to search, add, update, and manage bookmarks through LinkDing's REST API.

## Features

- **Search bookmarks** with flexible filtering (query, tags, archived status)
- **Add new bookmarks** with automatic metadata scraping
- **Update existing bookmarks** (title, description, notes, tags, etc.)
- **Delete bookmarks** by ID
- **Archive/unarchive bookmarks** for organization
- **Check URL status** to see if already bookmarked
- **List and filter by tags** for better organization
- **Retrieve bookmark details** by ID

## Prerequisites

- Python 3.12 or higher
- A running LinkDing instance (local or remote)
- LinkDing API token (available in LinkDing Settings)

## Key Features

- 🔒 **Security-First Design**: URL validation, token masking, optional write protection
- 🔄 **Resilient Networking**: Automatic retry with exponential backoff
- ⚡ **Performance Optimized**: Connection pooling, caching, rate limiting
- 📝 **Comprehensive Validation**: Input sanitization and type checking
- 🧪 **Well-Tested**: Unit tests with high coverage
- 📊 **Structured Logging**: Debug-friendly with contextual information

## Installation

### Quick Installation with uv (Recommended)

```bash
# Install using uv
uv pip install linkding-mcp-server

# Or install directly from GitHub
uv pip install git+https://github.com/jon-the-dev/linkding-mcp-server.git
```

### Installation with pip

```bash
# Install from PyPI
pip install linkding-mcp-server

# Or install from GitHub
pip install git+https://github.com/jon-the-dev/linkding-mcp-server.git
```

### Manual Installation from Source

1. **Clone the repository**:

   ```bash
   git clone https://github.com/jon-the-dev/linkding-mcp-server.git
   cd linkding-mcp-server
   ```

2. **Install with uv**:

   ```bash
   uv pip install -e .
   # For development
   uv pip install -e ".[dev]"
   ```

   Or with pip:

   ```bash
   pip install -e .
   # For development
   pip install -e ".[dev]"
   ```

## Configuration

### Initial Setup

After installation, run the setup command to configure your LinkDing connection:

```bash
linkding-mcp-setup
```

This will create a configuration file at `~/.linkding-mcp/config.env`.

### Manual Configuration

You can also configure the server using environment variables or a `.env` file:

```bash
# Create a .env file in your current directory
cp .env.sample .env
```

Edit `.env` and set your LinkDing configuration:

```env
# Required
LINKDING_URL=http://127.0.0.1:9090
LINKDING_API_TOKEN=your_api_token_here

# Security (important!)
LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=false  # Set to true to allow modifications

# Optional performance tuning
LINKDING_CACHE_TTL=300
LINKDING_MAX_CONNECTIONS=100
```

## Getting Your LinkDing API Token

1. Open your LinkDing web interface
2. Go to **Settings** (usually accessible via user menu)
3. Look for **API** or **Integrations** section
4. Copy the **API Token** (it will be a long string of characters)
5. Paste this token into your `.env` file as `LINKDING_API_TOKEN`

## Usage

### Running the Server

**Option 1: Using the installed command (recommended)**

```bash
# Run with uv
uv run linkding-mcp

# Or if installed globally
linkding-mcp
```

**Option 2: Using FastMCP CLI**

```bash
# For stdio transport (default)
fastmcp run linkding-mcp

# For HTTP transport (web deployment)
fastmcp run linkding-mcp --transport http --port 8000
```

**Option 3: Python module**

```bash
python -m linkding_mcp_server
```

### Available Tools

The server provides the following tools for LLM interaction:

#### 1. `search_bookmarks`

Search for bookmarks with various filters.

**Parameters:**

- `query` (optional): Search phrase for title, description, notes, URL
- `tag` (optional): Filter by specific tag name
- `limit` (default: 100): Maximum results to return
- `offset` (default: 0): Results to skip for pagination
- `archived` (default: false): Search archived bookmarks instead
- `unread_only` (default: false): Only return unread bookmarks

**Example:**

```python
# Search for bookmarks about Python
await client.call_tool("search_bookmarks", {"query": "python"})

# Get bookmarks with "tutorial" tag
await client.call_tool("search_bookmarks", {"tag": "tutorial"})

# Search archived bookmarks
await client.call_tool("search_bookmarks", {"archived": true, "limit": 50})
```

#### 2. `add_bookmark`

Add a new bookmark to LinkDing.

**Parameters:**

- `url` (required): The URL to bookmark
- `title` (optional): Custom title (auto-scraped if not provided)
- `description` (optional): Custom description (auto-scraped if not provided)
- `notes` (optional): Personal notes
- `tags` (optional): List of tag names
- `is_archived` (default: false): Save directly to archive
- `unread` (default: false): Mark as unread
- `shared` (default: false): Share with other users

**Example:**

```python
await client.call_tool("add_bookmark", {
    "url": "https://example.com",
    "title": "Example Site",
    "tags": ["example", "demo"],
    "notes": "Useful example website"
})
```

#### 3. `get_bookmark`

Retrieve a specific bookmark by ID.

**Parameters:**

- `bookmark_id` (required): The bookmark ID

#### 4. `update_bookmark`

Update an existing bookmark.

**Parameters:**

- `bookmark_id` (required): The bookmark ID
- All other parameters from `add_bookmark` (all optional)

#### 5. `delete_bookmark`

Delete a bookmark by ID.

**Parameters:**

- `bookmark_id` (required): The bookmark ID

#### 6. `archive_bookmark` / `unarchive_bookmark`

Archive or unarchive a bookmark.

**Parameters:**

- `bookmark_id` (required): The bookmark ID

#### 7. `check_url`

Check if a URL is already bookmarked and get metadata.

**Parameters:**

- `url` (required): The URL to check

#### 8. `list_tags`

List all available tags.

**Parameters:**

- `limit` (default: 100): Maximum tags to return
- `offset` (default: 0): Tags to skip for pagination

#### 9. `list_bookmarks_by_tag`

List bookmarks filtered by a specific tag.

**Parameters:**

- `tag_name` (required): Name of the tag to filter by
- `limit` (default: 100): Maximum bookmarks to return
- `offset` (default: 0): Bookmarks to skip for pagination

## Integration with Claude Desktop

To use this server with Claude Desktop, add it to your Claude configuration:

1. **Find your Claude config file**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

2. **Add the server configuration**:

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

   Or if you have it installed globally:

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

3. **Restart Claude Desktop**

## Development

### Project Structure

```
linkding-mcp-server/
├── src/
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration management
│   ├── models.py          # Pydantic data models
│   ├── client.py          # HTTP client with retry logic
│   ├── tools.py           # MCP tool implementations
│   └── server.py          # Main server entry point
├── tests/
│   ├── test_models.py     # Model validation tests
│   ├── test_client.py     # Client functionality tests
│   └── test_config.py     # Configuration tests
├── linkding_server.py     # Legacy entry point
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pytest.ini            # Test configuration
├── Makefile              # Development commands
├── .env.sample           # Environment template
├── .env                  # Your local config (not in git)
└── README.md             # This file
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_models.py
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check
```

### Adding New Features

The server is built using the FastMCP framework. To add new tools:

1. Define the tool function with proper type hints
2. Add the `@mcp.tool` decorator
3. Include comprehensive docstring with parameter descriptions
4. Handle errors gracefully and return meaningful messages
5. Follow the existing patterns for API calls and response handling

### Configuration Options

The server supports extensive configuration through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LINKDING_URL` | `http://127.0.0.1:9090` | LinkDing server URL |
| `LINKDING_API_TOKEN` | Required | API authentication token |
| `LINKDING_ENABLE_DESTRUCTIVE_ACTIONS` | `false` | Allow write operations |
| `LINKDING_REQUEST_TIMEOUT` | `30` | Request timeout (seconds) |
| `LINKDING_MAX_RETRIES` | `3` | Retry attempts on failure |
| `LINKDING_CACHE_TTL` | `300` | Cache duration (seconds) |
| `LINKDING_RATE_LIMIT_CALLS` | `100` | API calls per period |
| `LINKDING_RATE_LIMIT_PERIOD` | `60` | Rate limit window (seconds) |
| `LINKDING_LOG_LEVEL` | `INFO` | Logging verbosity |

See `.env.sample` for complete configuration options.

### Security Features

- **URL Validation**: Prevents SSRF attacks through strict URL validation
- **Token Masking**: API tokens are masked in logs and error messages
- **Write Protection**: Destructive actions disabled by default
- **Input Sanitization**: All inputs validated and sanitized
- **Rate Limiting**: Prevents API abuse

### Error Handling

The server includes comprehensive error handling:

- **Automatic Retry**: Network errors trigger exponential backoff retry
- **Graceful Degradation**: Falls back to cached data when possible
- **Detailed Logging**: Structured logs with context for debugging
- **User-Friendly Messages**: Clear error messages without exposing sensitive data

## Performance Optimization

The server is optimized for performance:

- **Connection Pooling**: Reuses HTTP connections efficiently
- **Smart Caching**: Caches frequently accessed data like tags
- **Async Operations**: Non-blocking I/O for better concurrency
- **Rate Limiting**: Prevents overwhelming the LinkDing server

## Troubleshooting

### Common Issues

1. **"LINKDING_API_TOKEN environment variable is required"**
   - Make sure you've created a `.env` file with your API token
   - Verify the token is correct (check LinkDing Settings)

2. **Connection errors**
   - Verify LinkDing is running and accessible at the configured URL
   - Check if the URL includes the correct port (e.g., `:9090`)
   - Ensure there are no firewall issues

3. **"HTTP 401: Unauthorized"**
   - Your API token is invalid or expired
   - Generate a new token in LinkDing Settings

4. **"HTTP 404: Not Found"**
   - The LinkDing API endpoint might have changed
   - Verify your LinkDing version is compatible

### Debug Mode

Enable debug logging by setting `DEBUG=true` in your `.env` file. This will provide more detailed information about API requests and responses.

## API Compatibility

This server is compatible with LinkDing API v1. It has been tested with LinkDing versions 1.25+ but should work with most recent versions.

## Contributing

Contributions are welcome! Please:

1. Follow the existing code style and patterns
2. Add proper type hints and docstrings
3. Include error handling for new features
4. Update the README if adding new tools
5. Test with a real LinkDing instance

## License

This project is open source. Please check the repository for license details.

## Related Projects

- [LinkDing](https://github.com/sissbruecker/linkding) - The bookmark manager this server connects to
- [FastMCP](https://github.com/jlowin/fastmcp) - The MCP framework used to build this server
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
