# Installation

This guide will walk you through installing and setting up the LinkDing MCP Server.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12 or higher** installed on your system
- A **running LinkDing instance** (local or remote)
- **LinkDing API token** (see [Getting Your API Token](#getting-your-api-token))

## Installation Methods

### Quick Install from PyPI (Recommended)

The easiest way to install is via pip:

```bash
pip install linkding-mcp-server
```

Or using uv (faster):

```bash
uv pip install linkding-mcp-server
```

### Install from Source

For development or latest features:

```bash
git clone https://github.com/jon-the-dev/linkding-mcp-server.git
cd linkding-mcp-server
pip install -e .
```

## Initial Setup

After installation, run the interactive setup wizard:

```bash
linkding-mcp-setup
```

This will:

1. Check your Python version
2. Prompt for your LinkDing URL and API token
3. Ask about enabling destructive actions (add/update/delete)
4. Create a configuration file at `~/.linkding-mcp/config.env`
5. Test the connection to your LinkDing instance

### Manual Configuration

Alternatively, set environment variables directly:

```bash
export LINKDING_URL="http://127.0.0.1:9090"
export LINKDING_API_TOKEN="your_api_token_here"
export LINKDING_ENABLE_DESTRUCTIVE_ACTIONS="true"  # Optional: enable write operations
```

Or create a `.env` file in your working directory:

```env
LINKDING_URL=http://127.0.0.1:9090
LINKDING_API_TOKEN=your_api_token_here
LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=false
```

### SSL/TLS Configuration

For LinkDing instances behind self-signed certificates or custom CAs:

```bash
export LINKDING_VERIFY_SSL="true"          # Enable/disable SSL verification (default: true)
export LINKDING_SSL_CERT_PATH="/path/to/ca-bundle.crt"  # Path to custom CA bundle
```

!!! warning "Disabling SSL Verification"
    Setting `LINKDING_VERIFY_SSL=false` disables certificate checks entirely. Only use this for local development or trusted networks.

### Cache Configuration

The server uses LRU caching for tag lookups and other repeated requests:

```bash
export LINKDING_CACHE_MAX_SIZE="100"  # Maximum cache entries before LRU eviction (default: 100)
```

## Getting Your API Token

To get your LinkDing API token:

1. **Open your LinkDing web interface**
2. **Navigate to Settings** (usually accessible via the user menu in the top-right)
3. **Find the API section** (may be under "Integrations" or "API")
4. **Copy the API Token** - it will be a long string of characters
5. **Paste the token** into your configuration

!!! warning "Keep Your Token Secure"
    Your API token provides full access to your LinkDing bookmarks. Keep it secure and never commit it to version control.

## Verify Installation

Test that everything is working correctly:

```bash
# Check the CLI is available
linkding-mcp --help

# Or run a quick test
python -c "from linkding_mcp_server import __version__; print(f'Version: {__version__}')"
```

## Running the Server

You have several options for running the server:

### Option 1: CLI Command (Recommended)

```bash
linkding-mcp
```

### Option 2: Using uv

```bash
uv run linkding-mcp
```

### Option 3: Python Module

```bash
python -m linkding_mcp_server
```

### Option 4: HTTP Transport (for web deployment)

```bash
fastmcp run linkding-mcp --transport http --port 8000
```

## Docker Installation (Optional)

If you prefer using Docker:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install linkding-mcp-server

EXPOSE 8000

CMD ["fastmcp", "run", "linkding-mcp", "--transport", "http", "--port", "8000"]
```

Build and run:

```bash
docker build -t linkding-mcp-server .
docker run -p 8000:8000 \
  -e LINKDING_URL="http://host.docker.internal:9090" \
  -e LINKDING_API_TOKEN="your_token" \
  linkding-mcp-server
```

## Troubleshooting Installation

### Common Issues

**"LINKDING_API_TOKEN environment variable is required"**
: Run `linkding-mcp-setup` to configure your credentials, or set the environment variable manually

**"Module not found" errors**
: Ensure the package is installed: `pip install linkding-mcp-server`

**"Connection refused" errors**
: Verify your LinkDing instance is running and accessible at the configured URL

**"HTTP 401: Unauthorized"**
: Your API token is invalid - generate a new one in LinkDing Settings

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
export LINKDING_LOG_LEVEL=DEBUG
linkding-mcp
```

This will provide detailed information about API requests and responses.

## Next Steps

- [Configuration](configuration.md) - Learn about all configuration options
- [Quick Start](quickstart.md) - Start using the server
- [Claude Desktop Integration](integration/claude.md) - Set up with Claude Desktop
