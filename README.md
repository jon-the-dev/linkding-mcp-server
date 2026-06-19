# LinkDing MCP Server

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

## Installation

**Install from PyPI:**

```bash
pip install linkding-mcp-server
```

**Configure environment variables:**

Create a `.env` file with your LinkDing configuration:

```env
LINKDING_URL=http://127.0.0.1:9090
LINKDING_API_TOKEN=your_api_token_here
DEBUG=false
```

Or run the interactive setup helper:

```bash
linkding-mcp-setup
```

## Getting Your LinkDing API Token

1. Open your LinkDing web interface
2. Go to **Settings** (usually accessible via user menu)
3. Look for **API** or **Integrations** section
4. Copy the **API Token** (it will be a long string of characters)
5. Paste this token into your `.env` file as `LINKDING_API_TOKEN`

## Usage

### Running the Server

**Option 1: Console script (recommended)**

```bash
linkding-mcp-server
```

**Option 2: Direct Python execution**

```bash
python -m linkding_mcp_server.server
```

**Option 3: HTTP transport for web deployment**

```bash
fastmcp run linkding_mcp_server.server:main --transport http --port 8000
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
         "command": "linkding-mcp-server",
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
├── linkding_mcp_server/    # Installable Python package
│   ├── __init__.py         # Package version and exports
│   ├── config.py           # Settings class and singleton
│   ├── client.py           # LinkDingClient HTTP wrapper
│   ├── models.py           # Pydantic models
│   ├── tools.py            # MCP tool registrations
│   ├── server.py           # main() entry point
│   └── setup.py            # Interactive setup helper
├── tests/                  # Test suite
├── pyproject.toml          # Package metadata and build config
├── requirements.txt        # Runtime dependencies
├── .env.sample             # Environment variables template
├── .env                    # Your local environment (not in git)
└── README.md               # This file
```

### Adding New Features

The server is built using the FastMCP framework. To add new tools:

1. Define the tool function with proper type hints
2. Add the `@mcp.tool` decorator
3. Include comprehensive docstring with parameter descriptions
4. Handle errors gracefully and return meaningful messages
5. Follow the existing patterns for API calls and response handling

### Error Handling

The server includes comprehensive error handling for:

- Network connectivity issues
- LinkDing API errors
- Invalid parameters
- Missing configuration

All errors are returned as descriptive strings that help users understand what went wrong.

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

This project is licensed under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later). See [LICENSE](LICENSE) for details.

## Related Projects

- [LinkDing](https://github.com/sissbruecker/linkding) - The bookmark manager this server connects to
- [FastMCP](https://github.com/jlowin/fastmcp) - The MCP framework used to build this server
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
