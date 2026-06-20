# Configuration

The LinkDing MCP Server is configured through environment variables. This guide covers all available configuration options.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LINKDING_API_TOKEN` | Your LinkDing API token | `abcd1234efgh5678...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LINKDING_URL` | `http://127.0.0.1:9090` | URL of your LinkDing instance |
| `LINKDING_ENABLE_DESTRUCTIVE_ACTIONS` | `false` | Enable bookmark modifications (add, update, delete, archive) |
| `LINKDING_VERIFY_SSL` | `true` | Enable SSL/TLS certificate verification |
| `LINKDING_SSL_CERT_PATH` | _(unset)_ | Path to a custom CA bundle or certificate file |
| `DEBUG` | `false` | Enable debug logging |

## Configuration File

Create a `.env` file in the project root:

```env
# LinkDing Configuration
LINKDING_URL=http://127.0.0.1:9090
LINKDING_API_TOKEN=your_api_token_here

# Security Settings
LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=false

# Optional Settings
DEBUG=false
```

## Security Configuration

### Destructive Actions Protection

By default, the LinkDing MCP Server operates in **read-only mode** for security. This means only safe operations are allowed:

**Always Allowed (Safe Actions):**
- `search_bookmarks` - Search your bookmarks
- `get_bookmark` - Retrieve bookmark details
- `list_tags` - List available tags
- `list_bookmarks_by_tag` - Filter bookmarks by tag
- `check_url` - Check if URL is already bookmarked

**Requires Explicit Enable (Destructive Actions):**
- `add_bookmark` - Create new bookmarks
- `update_bookmark` - Modify existing bookmarks
- `delete_bookmark` - Permanently delete bookmarks
- `archive_bookmark` - Archive bookmarks
- `unarchive_bookmark` - Unarchive bookmarks

### Enabling Destructive Actions

To enable bookmark modifications, set the environment variable:

```env
LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=true
```

!!! warning "Security Consideration"
    Only enable destructive actions if you trust the MCP client and understand that it will have full access to modify your bookmarks. MCP servers are powerful and should be used with appropriate caution.

### Error Messages

When destructive actions are attempted but not enabled, you'll see:

```
Error: Destructive actions are disabled for security. 
To enable bookmark modifications, set LINKDING_ENABLE_DESTRUCTIVE_ACTIONS=true 
in your environment variables or .env file. 
This includes: add, update, delete, archive, and unarchive operations.
```

### SSL/TLS Verification

The server verifies SSL/TLS certificates for all HTTPS connections by default. Two environment variables control this behavior.

#### `LINKDING_VERIFY_SSL`

| Value | Behavior |
|-------|----------|
| `true` (default) | Verify certificates using the system CA bundle |
| `false` | Skip certificate verification entirely |

```env
# Default — secure
LINKDING_VERIFY_SSL=true

# Disable verification (see warning below)
LINKDING_VERIFY_SSL=false
```

!!! danger "Disabling SSL verification is a security risk"
    Setting `LINKDING_VERIFY_SSL=false` means the server will accept any certificate
    presented by the LinkDing host, including forged ones. This exposes all traffic
    (including your API token) to man-in-the-middle attacks. Only use this setting
    on fully trusted, isolated networks where you control both endpoints and cannot
    install a proper certificate. A WARNING is emitted at startup when verification
    is disabled.

#### `LINKDING_SSL_CERT_PATH`

Specifies a custom CA bundle or certificate file (PEM format). Use this when your LinkDing instance uses a private or internal certificate authority rather than a publicly trusted one.

```env
LINKDING_SSL_CERT_PATH=/etc/ssl/certs/my-internal-ca.pem
```

Leave this variable unset to use the system default CA bundle.

**Precedence:**

1. If `LINKDING_VERIFY_SSL=false`, verification is skipped entirely (cert path is ignored).
2. If `LINKDING_SSL_CERT_PATH` is set, that CA bundle is used for verification.
3. Otherwise, the system default CA bundle is used.

**Example — self-hosted instance with internal CA:**

```env
LINKDING_URL=https://bookmarks.internal.example.com
LINKDING_API_TOKEN=your_token_here
LINKDING_SSL_CERT_PATH=/usr/local/share/ca-certificates/internal-ca.crt
```

## LinkDing URL Configuration

The `LINKDING_URL` should point to your LinkDing instance:

### Local Installation
```env
LINKDING_URL=http://127.0.0.1:9090
```

### Remote Server
```env
LINKDING_URL=https://bookmarks.example.com
```

### Custom Port
```env
LINKDING_URL=http://192.168.1.100:8080
```

!!! note "URL Format"
    - Include the protocol (`http://` or `https://`)
    - Include the port if not using standard ports (80/443)
    - Do not include trailing slashes

## Debug Configuration

Enable debug mode for troubleshooting:

```env
DEBUG=true
```

Debug mode provides:

- Detailed API request/response logging
- Enhanced error messages
- Performance timing information
- Connection diagnostics

!!! warning "Production Usage"
    Disable debug mode in production as it may log sensitive information and impact performance.

## API Token Security

### Getting Your Token

1. Log into your LinkDing web interface
2. Go to **Settings** → **API**
3. Copy the **API Token**

### Token Security Best Practices

- **Never commit tokens to version control**
- **Use environment-specific tokens** for different deployments
- **Rotate tokens regularly** for security
- **Limit token scope** if your LinkDing version supports it

### Environment-Specific Configuration

For different environments, use separate `.env` files:

#### Development (`.env.dev`)
```env
LINKDING_URL=http://127.0.0.1:9090
LINKDING_API_TOKEN=dev_token_here
DEBUG=true
```

#### Production (`.env.prod`)
```env
LINKDING_URL=https://bookmarks.company.com
LINKDING_API_TOKEN=prod_token_here
DEBUG=false
```

Load specific environment:
```bash
cp .env.prod .env
python linkding_server.py
```

## Docker Configuration

When using Docker, pass environment variables:

```bash
docker run -e LINKDING_URL=http://host.docker.internal:9090 \
           -e LINKDING_API_TOKEN=your_token \
           linkding-mcp-server
```

Or use an environment file:
```bash
docker run --env-file .env linkding-mcp-server
```

## Configuration Validation

The server validates configuration on startup:

- **Missing API token**: Server will not start
- **Invalid URL format**: Warning logged, may cause connection issues
- **Unreachable LinkDing**: Warning logged during first API call

## Advanced Configuration

### HTTP Client Settings

The server uses `httpx` for HTTP requests. While not directly configurable via environment variables, you can modify the client settings in the code:

```python
# In linkding_server.py
client = httpx.AsyncClient(
    timeout=30.0,  # Request timeout
    limits=httpx.Limits(max_connections=10)  # Connection limits
)
```

### Logging Configuration

Customize logging by modifying the logging setup:

```python
import logging

# Configure logging level
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Configuration Examples

### Home Lab Setup
```env
LINKDING_URL=http://192.168.1.100:9090
LINKDING_API_TOKEN=homelab_token_123
DEBUG=false
```

### Cloud Deployment
```env
LINKDING_URL=https://linkding.mydomain.com
LINKDING_API_TOKEN=cloud_secure_token_456
DEBUG=false
```

### Development Environment
```env
LINKDING_URL=http://localhost:9090
LINKDING_API_TOKEN=dev_token_789
DEBUG=true
```

## Troubleshooting Configuration

### Common Configuration Issues

**"LINKDING_API_TOKEN environment variable is required"**
: The API token is missing from your `.env` file

**Connection timeout errors**
: Check if `LINKDING_URL` is correct and LinkDing is running

**"HTTP 401: Unauthorized"**
: Your API token is invalid or expired

**"HTTP 404: Not Found"**
: The LinkDing URL or API endpoint is incorrect

### Testing Configuration

Use the test script to verify your configuration:

```bash
python test_server.py
```

This will test:
- Environment variable loading
- LinkDing connectivity
- API token validity
- Basic API functionality

## Next Steps

- [Quick Start](quickstart.md) - Start using the configured server
- [Troubleshooting](troubleshooting.md) - Resolve configuration issues
- [Integration](integration/claude.md) - Connect with MCP clients
