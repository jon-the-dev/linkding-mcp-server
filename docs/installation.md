# Installation

This guide will walk you through installing and setting up the LinkDing MCP Server.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12 or higher** installed on your system
- A **running LinkDing instance** (local or remote)
- **LinkDing API token** (see [Getting Your API Token](#getting-your-api-token))

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd linkding-mcp-server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

!!! tip "Virtual Environment Recommended"
    It's recommended to use a virtual environment to avoid conflicts:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

### 3. Configure Environment

Copy the sample environment file and configure it:

```bash
cp .env.sample .env
```

Edit the `.env` file with your LinkDing configuration:

```env
LINKDING_URL=http://127.0.0.1:9090
LINKDING_API_TOKEN=your_api_token_here
DEBUG=false
```

## Getting Your API Token

To get your LinkDing API token:

1. **Open your LinkDing web interface**
2. **Navigate to Settings** (usually accessible via the user menu in the top-right)
3. **Find the API section** (may be under "Integrations" or "API")
4. **Copy the API Token** - it will be a long string of characters
5. **Paste the token** into your `.env` file as `LINKDING_API_TOKEN`

!!! warning "Keep Your Token Secure"
    Your API token provides full access to your LinkDing bookmarks. Keep it secure and never commit it to version control.

## Verify Installation

Test that everything is working correctly:

```bash
python test_server.py
```

This will run basic connectivity tests to ensure your LinkDing instance is accessible.

## Running the Server

You have several options for running the server:

### Option 1: Direct Python Execution

```bash
python linkding_server.py
```

### Option 2: Using FastMCP CLI (Recommended)

```bash
fastmcp run linkding_server.py
```

### Option 3: HTTP Transport

For web deployment or remote access:

```bash
fastmcp run linkding_server.py --transport http --port 8000
```

## Docker Installation (Optional)

If you prefer using Docker:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["fastmcp", "run", "linkding_server.py", "--transport", "http", "--port", "8000"]
```

Build and run:

```bash
docker build -t linkding-mcp-server .
docker run -p 8000:8000 --env-file .env linkding-mcp-server
```

## Troubleshooting Installation

### Common Issues

**"LINKDING_API_TOKEN environment variable is required"**
: Make sure you've created a `.env` file with your API token

**"Module not found" errors**
: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Connection refused errors**
: Verify your LinkDing instance is running and accessible at the configured URL

**Permission denied errors**
: Make sure the script is executable: `chmod +x linkding_server.py`

### Debug Mode

Enable debug logging to troubleshoot issues:

```env
DEBUG=true
```

This will provide detailed information about API requests and responses.

## Next Steps

- [Configuration](configuration.md) - Learn about all configuration options
- [Quick Start](quickstart.md) - Start using the server
- [Tools Reference](tools/overview.md) - Explore available tools