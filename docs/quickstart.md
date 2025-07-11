# Quick Start

Get up and running with the LinkDing MCP Server in minutes.

## Prerequisites Check

Before starting, ensure you have:

- ✅ Python 3.12+ installed
- ✅ LinkDing instance running
- ✅ LinkDing API token ready

## 5-Minute Setup

### 1. Install and Configure

```bash
# Clone and enter directory
git clone <repository-url>
cd linkding-mcp-server

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env with your LinkDing URL and API token
```

### 2. Test Connection

```bash
python test_server.py
```

You should see output like:
```
✅ Environment variables loaded
✅ Connected to LinkDing
✅ API token is valid
✅ Basic functionality working
```

### 3. Start the Server

```bash
python linkding_server.py
```

The server will start and display available tools.

## First Steps with the Server

Once running, the server provides these tools for LLM interaction:

### Search Your Bookmarks

```python
# Search for bookmarks about Python
search_bookmarks(query="python")

# Find bookmarks with specific tags
search_bookmarks(tag="tutorial")

# Search archived bookmarks
search_bookmarks(archived=True, limit=10)
```

### Add a New Bookmark

```python
# Simple bookmark
add_bookmark(url="https://example.com")

# Bookmark with details
add_bookmark(
    url="https://python.org",
    title="Python Official Site",
    tags=["python", "programming"],
    notes="Official Python documentation and downloads"
)
```

### Check if URL is Already Bookmarked

```python
check_url(url="https://github.com")
```

### List Your Tags

```python
list_tags()
```

## Integration with Claude Desktop

To use with Claude Desktop, add this to your configuration:

### macOS Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "linkding": {
      "command": "python",
      "args": ["/path/to/linkding-mcp-server/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

### Windows Configuration

Edit `%APPDATA%/Claude/claude_desktop_config.json` with the same content.

After adding the configuration, restart Claude Desktop.

## Example Usage Scenarios

### Scenario 1: Research Session

```python
# Check if you've already bookmarked a site
check_url(url="https://research-site.com")

# Add it if not already bookmarked
add_bookmark(
    url="https://research-site.com",
    title="Important Research Paper",
    tags=["research", "ai", "papers"],
    notes="Key findings about neural networks"
)

# Find related bookmarks
search_bookmarks(tag="research")
```

### Scenario 2: Organizing Bookmarks

```python
# Find all untagged bookmarks
search_bookmarks(query="", limit=50)

# Update a bookmark with tags
update_bookmark(
    bookmark_id=123,
    tags=["web-dev", "javascript", "tutorial"]
)

# Archive old bookmarks
archive_bookmark(bookmark_id=456)
```

### Scenario 3: Content Discovery

```python
# List all your tags to see what you've collected
list_tags()

# Explore bookmarks by category
list_bookmarks_by_tag(tag_name="tutorials")

# Find bookmarks you haven't read yet
search_bookmarks(unread_only=True)
```

## Common Workflows

### Daily Bookmark Management

1. **Morning Review**: Check unread bookmarks
   ```python
   search_bookmarks(unread_only=True, limit=10)
   ```

2. **Add New Finds**: Bookmark interesting sites
   ```python
   add_bookmark(url="https://new-site.com", tags=["to-read"])
   ```

3. **Evening Cleanup**: Archive or tag processed bookmarks
   ```python
   update_bookmark(bookmark_id=123, tags=["processed", "useful"])
   archive_bookmark(bookmark_id=124)
   ```

### Research Project Organization

1. **Create Project Tags**: Use consistent tagging
   ```python
   add_bookmark(url="...", tags=["project-alpha", "research"])
   ```

2. **Find Project Resources**: Search by project tag
   ```python
   list_bookmarks_by_tag(tag_name="project-alpha")
   ```

3. **Archive Completed Projects**: Clean up when done
   ```python
   search_bookmarks(tag="project-alpha")
   # Then archive each bookmark
   ```

## Troubleshooting Quick Fixes

### Server Won't Start

```bash
# Check environment variables
cat .env

# Verify LinkDing is running
curl http://127.0.0.1:9090/api/bookmarks/ -H "Authorization: Token YOUR_TOKEN"

# Check Python version
python --version  # Should be 3.12+
```

### API Errors

```bash
# Enable debug mode
echo "DEBUG=true" >> .env

# Restart server to see detailed logs
python linkding_server.py
```

### Connection Issues

```bash
# Test LinkDing connectivity
python -c "
import httpx
response = httpx.get('http://127.0.0.1:9090')
print(f'Status: {response.status_code}')
"
```

## Next Steps

Now that you're up and running:

- **Explore Tools**: Check out the [Tools Reference](tools/overview.md) for detailed documentation
- **Advanced Configuration**: Learn about [Configuration Options](configuration.md)
- **Integration**: Set up [Claude Desktop Integration](integration/claude.md)
- **Development**: Contribute to the project with our [Development Guide](development/contributing.md)

## Getting Help

- **Common Issues**: Check [Troubleshooting](troubleshooting.md)
- **Questions**: See our [FAQ](faq.md)
- **Bugs**: Report on [GitHub Issues](https://github.com/your-username/linkding-mcp-server/issues)