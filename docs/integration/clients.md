# Other MCP Clients

The LinkDing MCP Server is compatible with any application that supports the Model Context Protocol. This guide covers integration with various MCP clients beyond Claude Desktop.

## Supported MCP Clients

### Desktop Applications

| Client | Platform | Status | Notes |
|--------|----------|--------|-------|
| Claude Desktop | macOS, Windows, Linux | ✅ Full Support | Primary integration target |
| Continue.dev | VS Code, JetBrains | ✅ Compatible | Code editor integration |
| Zed Editor | macOS, Linux | ✅ Compatible | Modern code editor |
| Cursor | macOS, Windows, Linux | ✅ Compatible | AI-powered code editor |

### Command Line Tools

| Tool | Platform | Status | Notes |
|------|----------|--------|-------|
| FastMCP CLI | Cross-platform | ✅ Full Support | Direct server execution |
| MCP Inspector | Cross-platform | ✅ Compatible | Development and testing |
| Custom Scripts | Cross-platform | ✅ Compatible | Python/Node.js integration |

### Web Applications

| Application | Status | Notes |
|-------------|--------|-------|
| MCP Web Clients | ✅ Compatible | HTTP transport support |
| Custom Web Apps | ✅ Compatible | REST API integration |

## FastMCP CLI Integration

FastMCP provides a command-line interface for interacting with MCP servers directly.

### Installation

```bash
pip install fastmcp
```

### Basic Usage

```bash
# Run the server directly
fastmcp run linkding_server.py

# Run with HTTP transport
fastmcp run linkding_server.py --transport http --port 8000

# Interactive mode
fastmcp dev linkding_server.py
```

### Configuration

Create a `fastmcp.yaml` configuration file:

```yaml
servers:
  linkding:
    command: python
    args: ["linkding_server.py"]
    env:
      LINKDING_URL: "http://127.0.0.1:9090"
      LINKDING_API_TOKEN: "your_token_here"
      DEBUG: "false"
```

Run with configuration:

```bash
fastmcp run --config fastmcp.yaml linkding
```

## Continue.dev Integration

Continue.dev is an AI coding assistant that supports MCP servers.

### VS Code Configuration

Add to your Continue configuration (`.continue/config.json`):

```json
{
  "models": [...],
  "mcpServers": {
    "linkding": {
      "command": "python",
      "args": ["/absolute/path/to/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Usage in Continue

```
// In VS Code with Continue
@linkding search for python tutorials

@linkding add bookmark https://python.org with tags python,documentation
```

## Zed Editor Integration

Zed is a modern code editor with MCP support.

### Configuration

Add to your Zed settings (`~/.config/zed/settings.json`):

```json
{
  "assistant": {
    "mcp_servers": {
      "linkding": {
        "command": "python",
        "args": ["/path/to/linkding_server.py"],
        "env": {
          "LINKDING_URL": "http://127.0.0.1:9090",
          "LINKDING_API_TOKEN": "your_token"
        }
      }
    }
  }
}
```

### Usage

Use the assistant panel in Zed to interact with your bookmarks while coding.

## Cursor Integration

Cursor is an AI-powered code editor with MCP support.

### Configuration

Add to Cursor's MCP configuration:

```json
{
  "mcpServers": {
    "linkding": {
      "command": "python",
      "args": ["/absolute/path/to/linkding_server.py"],
      "env": {
        "LINKDING_URL": "http://127.0.0.1:9090",
        "LINKDING_API_TOKEN": "your_token"
      }
    }
  }
}
```

## HTTP Transport Integration

For web applications or remote access, use HTTP transport.

### Server Setup

```bash
# Start server with HTTP transport
fastmcp run linkding_server.py --transport http --port 8000 --host 0.0.0.0
```

### Client Integration

#### JavaScript/Node.js

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
  command: 'python',
  args: ['/path/to/linkding_server.py']
});

const client = new Client({
  name: "linkding-client",
  version: "1.0.0"
}, {
  capabilities: {}
});

await client.connect(transport);

// Use the client
const result = await client.callTool("search_bookmarks", {
  query: "python",
  limit: 10
});
```

#### Python

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["linkding_server.py"],
        env={
            "LINKDING_URL": "http://127.0.0.1:9090",
            "LINKDING_API_TOKEN": "your_token"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools])
            
            # Search bookmarks
            result = await session.call_tool("search_bookmarks", {
                "query": "python",
                "limit": 5
            })
            print("Search results:", result)

asyncio.run(main())
```

## Custom Integration Examples

### Slack Bot Integration

```python
import asyncio
from slack_bolt.async_app import AsyncApp
from mcp.client.stdio import stdio_client

app = AsyncApp(token="your-slack-token")

@app.command("/bookmark")
async def bookmark_command(ack, respond, command):
    await ack()
    
    url = command['text']
    
    # Connect to LinkDing MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["linkding_server.py"],
        env={"LINKDING_URL": "...", "LINKDING_API_TOKEN": "..."}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Check if URL already exists
            check_result = await session.call_tool("check_url", {"url": url})
            
            if check_result['is_bookmarked']:
                await respond(f"URL already bookmarked: {check_result['bookmark']['title']}")
            else:
                # Add bookmark
                result = await session.call_tool("add_bookmark", {
                    "url": url,
                    "tags": ["slack", "team-shared"]
                })
                await respond(f"Bookmarked: {result['title']}")
```

### Discord Bot Integration

```python
import discord
from discord.ext import commands
from mcp.client.stdio import stdio_client

bot = commands.Bot(command_prefix='!')

@bot.command(name='search')
async def search_bookmarks(ctx, *, query):
    server_params = StdioServerParameters(
        command="python",
        args=["linkding_server.py"],
        env={"LINKDING_URL": "...", "LINKDING_API_TOKEN": "..."}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool("search_bookmarks", {
                "query": query,
                "limit": 5
            })
            
            if result:
                embed = discord.Embed(title=f"Bookmarks for '{query}'")
                for bookmark in result[:5]:
                    embed.add_field(
                        name=bookmark['title'],
                        value=bookmark['url'],
                        inline=False
                    )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No bookmarks found for '{query}'")
```

### Web Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>LinkDing Dashboard</title>
</head>
<body>
    <div id="app">
        <h1>My Bookmarks</h1>
        <input type="text" id="search" placeholder="Search bookmarks...">
        <div id="results"></div>
    </div>

    <script>
        async function searchBookmarks(query) {
            const response = await fetch('http://localhost:8000/call_tool', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: 'search_bookmarks',
                    arguments: {query: query, limit: 20}
                })
            });
            
            const result = await response.json();
            displayResults(result.content);
        }
        
        function displayResults(bookmarks) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = bookmarks.map(bookmark => `
                <div class="bookmark">
                    <h3><a href="${bookmark.url}">${bookmark.title}</a></h3>
                    <p>${bookmark.description}</p>
                    <div class="tags">${bookmark.tag_names.join(', ')}</div>
                </div>
            `).join('');
        }
        
        document.getElementById('search').addEventListener('input', (e) => {
            if (e.target.value.length > 2) {
                searchBookmarks(e.target.value);
            }
        });
    </script>
</body>
</html>
```

## Configuration Best Practices

### Environment Management

Use environment-specific configurations:

```bash
# Development
export LINKDING_URL="http://localhost:9090"
export LINKDING_API_TOKEN="dev_token"

# Production
export LINKDING_URL="https://bookmarks.company.com"
export LINKDING_API_TOKEN="prod_token"
```

### Security Considerations

#### Token Management
- Use different tokens for different clients
- Rotate tokens regularly
- Never commit tokens to version control
- Use environment variables or secure vaults

#### Network Security
- Use HTTPS for remote LinkDing instances
- Consider VPN for internal deployments
- Implement rate limiting for public endpoints
- Monitor API usage for anomalies

### Performance Optimization

#### Connection Pooling
```python
# For high-volume applications
import asyncio
from asyncio import Semaphore

# Limit concurrent connections
connection_semaphore = Semaphore(5)

async def rate_limited_call(session, tool_name, args):
    async with connection_semaphore:
        return await session.call_tool(tool_name, args)
```

#### Caching
```python
import time
from functools import lru_cache

# Cache tag lists (they don't change often)
@lru_cache(maxsize=1)
def get_cached_tags():
    # Implementation with timestamp checking
    pass
```

## Troubleshooting Multi-Client Issues

### Common Problems

#### Port Conflicts
```bash
# Check what's using the port
lsof -i :8000

# Use different port
fastmcp run linkding_server.py --transport http --port 8001
```

#### Permission Issues
```bash
# Ensure script is executable
chmod +x linkding_server.py

# Check Python path
which python
```

#### Environment Variable Conflicts
```bash
# Clear environment
unset LINKDING_URL LINKDING_API_TOKEN

# Set explicitly
export LINKDING_URL="http://127.0.0.1:9090"
export LINKDING_API_TOKEN="your_token"
```

### Debug Multiple Clients

#### Enable Debug Mode
```bash
export DEBUG=true
fastmcp run linkding_server.py
```

#### Monitor Connections
```bash
# Watch server logs
tail -f /var/log/linkding-mcp.log

# Monitor network connections
netstat -an | grep 8000
```

## Next Steps

- **[API Reference](../api/reference.md)** - Technical implementation details
- **[Development Guide](../development/contributing.md)** - Contribute to the project
- **[Troubleshooting](../troubleshooting.md)** - Resolve common issues