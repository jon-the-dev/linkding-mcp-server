# API Reference

Technical reference for the LinkDing MCP Server implementation, data models, and API interactions.

## Server Architecture

The LinkDing MCP Server is built using the FastMCP framework and follows the Model Context Protocol specification.

### Core Components

```python
# Main server class
class LinkDingMCPServer:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.base_url = LINKDING_URL
        self.headers = {"Authorization": f"Token {LINKDING_API_TOKEN}"}
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastmcp` | Latest | MCP server framework |
| `httpx` | Latest | HTTP client for LinkDing API |
| `pydantic` | Latest | Data validation and serialization |
| `python-dotenv` | Latest | Environment variable management |

## Data Models

### Bookmark Model

```python
class Bookmark(BaseModel):
    """Represents a LinkDing bookmark"""
    id: int
    url: str
    title: str
    description: str = ""
    notes: str = ""
    web_archive_snapshot_url: Optional[str] = None
    favicon_url: Optional[str] = None
    preview_image_url: Optional[str] = None
    is_archived: bool = False
    unread: bool = False
    shared: bool = False
    date_added: datetime
    date_modified: datetime
    tag_names: List[str] = []
```

### Tag Model

```python
class Tag(BaseModel):
    """Represents a LinkDing tag"""
    id: int
    name: str
    bookmark_count: int
```

### Search Response Model

```python
class SearchResponse(BaseModel):
    """Response from bookmark search operations"""
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Bookmark]
```

## Tool Specifications

### search_bookmarks

**Function Signature:**
```python
@mcp.tool()
async def search_bookmarks(
    query: str = "",
    tag: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    archived: bool = False,
    unread_only: bool = False
) -> str:
```

**Parameters:**
- `query` (string, optional): Search phrase for title, description, notes, URL
- `tag` (string, optional): Filter by specific tag name
- `limit` (integer, default: 100): Maximum results to return
- `offset` (integer, default: 0): Results to skip for pagination
- `archived` (boolean, default: false): Search archived bookmarks instead
- `unread_only` (boolean, default: false): Only return unread bookmarks

**Returns:** JSON string containing search results

**LinkDing API Endpoint:** `GET /api/bookmarks/`

**Query Parameters:**
```python
params = {
    "q": query,
    "tag": tag,
    "limit": limit,
    "offset": offset,
    "archived": archived,
    "unread": unread_only
}
```

### add_bookmark

**Function Signature:**
```python
@mcp.tool()
async def add_bookmark(
    url: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
    is_archived: bool = False,
    unread: bool = False,
    shared: bool = False
) -> str:
```

**Parameters:**
- `url` (string, required): The URL to bookmark
- `title` (string, optional): Custom title (auto-scraped if not provided)
- `description` (string, optional): Custom description (auto-scraped if not provided)
- `notes` (string, optional): Personal notes
- `tags` (array, optional): List of tag names
- `is_archived` (boolean, default: false): Save directly to archive
- `unread` (boolean, default: false): Mark as unread
- `shared` (boolean, default: false): Share with other users

**Returns:** JSON string containing created bookmark data

**LinkDing API Endpoint:** `POST /api/bookmarks/`

**Request Body:**
```python
data = {
    "url": url,
    "title": title,
    "description": description,
    "notes": notes,
    "tag_names": tags or [],
    "is_archived": is_archived,
    "unread": unread,
    "shared": shared
}
```

### get_bookmark

**Function Signature:**
```python
@mcp.tool()
async def get_bookmark(bookmark_id: int) -> str:
```

**Parameters:**
- `bookmark_id` (integer, required): The bookmark ID

**Returns:** JSON string containing bookmark data

**LinkDing API Endpoint:** `GET /api/bookmarks/{id}/`

### update_bookmark

**Function Signature:**
```python
@mcp.tool()
async def update_bookmark(
    bookmark_id: int,
    url: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
    is_archived: Optional[bool] = None,
    unread: Optional[bool] = None,
    shared: Optional[bool] = None
) -> str:
```

**Parameters:**
- `bookmark_id` (integer, required): The bookmark ID
- All other parameters are optional and will only update if provided

**Returns:** JSON string containing updated bookmark data

**LinkDing API Endpoint:** `PATCH /api/bookmarks/{id}/`

### delete_bookmark

**Function Signature:**
```python
@mcp.tool()
async def delete_bookmark(bookmark_id: int) -> str:
```

**Parameters:**
- `bookmark_id` (integer, required): The bookmark ID

**Returns:** Success or error message

**LinkDing API Endpoint:** `DELETE /api/bookmarks/{id}/`

### archive_bookmark

**Function Signature:**
```python
@mcp.tool()
async def archive_bookmark(bookmark_id: int) -> str:
```

**Parameters:**
- `bookmark_id` (integer, required): The bookmark ID

**Returns:** Success or error message

**Implementation:** Uses `update_bookmark` with `is_archived=True`

### unarchive_bookmark

**Function Signature:**
```python
@mcp.tool()
async def unarchive_bookmark(bookmark_id: int) -> str:
```

**Parameters:**
- `bookmark_id` (integer, required): The bookmark ID

**Returns:** Success or error message

**Implementation:** Uses `update_bookmark` with `is_archived=False`

### check_url

**Function Signature:**
```python
@mcp.tool()
async def check_url(url: str) -> str:
```

**Parameters:**
- `url` (string, required): The URL to check

**Returns:** JSON string containing bookmark status and metadata

**LinkDing API Endpoint:** `GET /api/bookmarks/check-url/`

**Query Parameters:**
```python
params = {"url": url}
```

### list_tags

**Function Signature:**
```python
@mcp.tool()
async def list_tags(
    limit: int = 100,
    offset: int = 0
) -> str:
```

**Parameters:**
- `limit` (integer, default: 100): Maximum tags to return
- `offset` (integer, default: 0): Tags to skip for pagination

**Returns:** JSON string containing list of tags

**LinkDing API Endpoint:** `GET /api/tags/`

### list_bookmarks_by_tag

**Function Signature:**
```python
@mcp.tool()
async def list_bookmarks_by_tag(
    tag_name: str,
    limit: int = 100,
    offset: int = 0
) -> str:
```

**Parameters:**
- `tag_name` (string, required): Name of the tag to filter by
- `limit` (integer, default: 100): Maximum bookmarks to return
- `offset` (integer, default: 0): Bookmarks to skip for pagination

**Returns:** JSON string containing filtered bookmarks

**Implementation:** Uses `search_bookmarks` with `tag` parameter

## HTTP Client Configuration

### Default Configuration

```python
client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(
        max_keepalive_connections=5,
        max_connections=10
    ),
    headers={
        "Authorization": f"Token {LINKDING_API_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "LinkDing-MCP-Server/1.0"
    }
)
```

### Request Handling

```python
async def make_request(method: str, endpoint: str, **kwargs) -> dict:
    """Make HTTP request to LinkDing API"""
    url = f"{LINKDING_URL}/api{endpoint}"
    
    try:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise
```

## Error Handling

### Layer Contract

Direct Python callers handle client exceptions:

```python
from linkding_mcp_server.client import LinkDingClient, LinkDingError

try:
    async with LinkDingClient(settings) as client:
        bookmark = await client.get_bookmark(123)
except LinkDingError as error:
    logger.warning("linkding_request_failed", error=str(error))
```

MCP callers receive the translated error as tool content:

```python
result = await mcp_client.call_tool("get_bookmark", {"bookmark_id": 123})
# result.content[0].text == "Error: Bookmark with ID 123 not found"
```

`RateLimitError` is a `LinkDingError`, so direct and MCP callers use the same
contract for API rate-limit responses.

### HTTP Status Codes

| Status Code | Meaning | Handling |
|-------------|---------|----------|
| 200 | Success | Return data |
| 201 | Created | Return created resource |
| 400 | Bad Request | Return validation error |
| 401 | Unauthorized | Return authentication error |
| 404 | Not Found | Return "not found" message |
| 500 | Server Error | Return generic error message |

## Environment Configuration

### Required Variables

```python
LINKDING_URL = os.getenv("LINKDING_URL", "http://127.0.0.1:9090")
LINKDING_API_TOKEN = os.getenv("LINKDING_API_TOKEN")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

### Validation

```python
def validate_config():
    """Validate configuration on startup"""
    if not LINKDING_API_TOKEN:
        raise ValueError("LINKDING_API_TOKEN environment variable is required")
    
    if not LINKDING_URL.startswith(('http://', 'https://')):
        logger.warning("LINKDING_URL should include protocol (http:// or https://)")
    
    # Remove trailing slash
    LINKDING_URL = LINKDING_URL.rstrip("/")
```

## Logging Configuration

### Setup

```python
import logging

# Configure logging
log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('linkding-mcp.log') if DEBUG else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Debug Logging

```python
if DEBUG:
    logger.debug(f"Making request: {method} {url}")
    logger.debug(f"Request params: {params}")
    logger.debug(f"Request data: {data}")
    logger.debug(f"Response: {response.text}")
```

## Performance Considerations

### Connection Pooling

```python
# Reuse HTTP client instance
client = httpx.AsyncClient()

# Close client on shutdown
async def cleanup():
    await client.aclose()
```

### Rate Limiting

```python
import asyncio
from asyncio import Semaphore

# Limit concurrent requests
rate_limiter = Semaphore(5)

async def rate_limited_request(*args, **kwargs):
    async with rate_limiter:
        return await make_request(*args, **kwargs)
```

### Caching

```python
from functools import lru_cache
import time

# Cache tag list (changes infrequently)
@lru_cache(maxsize=1)
def get_cached_tags():
    return list_tags()

# Cache with TTL
tag_cache = {"data": None, "timestamp": 0}
TAG_CACHE_TTL = 300  # 5 minutes

async def get_tags_with_cache():
    now = time.time()
    if (tag_cache["data"] is None or 
        now - tag_cache["timestamp"] > TAG_CACHE_TTL):
        tag_cache["data"] = await list_tags()
        tag_cache["timestamp"] = now
    return tag_cache["data"]
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_search_bookmarks():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "count": 1,
            "results": [{"id": 1, "title": "Test", "url": "https://test.com"}]
        }
        
        result = await search_bookmarks(query="test")
        assert "Test" in result

@pytest.mark.asyncio
async def test_add_bookmark():
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "id": 1,
            "title": "New Bookmark",
            "url": "https://example.com"
        }
        
        result = await add_bookmark(url="https://example.com")
        assert "New Bookmark" in result
```

### Integration Tests

```python
@pytest.mark.integration
async def test_real_linkding_connection():
    """Test against real LinkDing instance"""
    # Requires LINKDING_URL and LINKDING_API_TOKEN
    result = await search_bookmarks(limit=1)
    assert isinstance(result, str)
    
    # Parse JSON to verify structure
    data = json.loads(result)
    assert "count" in data
    assert "results" in data
```

## Security Considerations

### API Token Handling

```python
# Never log tokens
def safe_log_headers(headers):
    safe_headers = headers.copy()
    if "Authorization" in safe_headers:
        safe_headers["Authorization"] = "Token [REDACTED]"
    return safe_headers

logger.debug(f"Request headers: {safe_log_headers(headers)}")
```

### Input Validation

```python
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_bookmark_id(bookmark_id: int) -> bool:
    """Validate bookmark ID"""
    return isinstance(bookmark_id, int) and bookmark_id > 0
```

### HTTPS Enforcement

```python
def ensure_https(url: str) -> str:
    """Ensure URL uses HTTPS in production"""
    if not DEBUG and url.startswith("http://"):
        logger.warning("Using HTTP in production is not recommended")
    return url
```

## Deployment

### Production Configuration

```python
# Production settings
if not DEBUG:
    # Disable detailed error messages
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Use connection pooling
    client = httpx.AsyncClient(
        limits=httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100
        )
    )
```

### Health Checks

```python
async def health_check() -> bool:
    """Check if LinkDing is accessible"""
    try:
        response = await client.get(f"{LINKDING_URL}/api/bookmarks/", 
                                  params={"limit": 1})
        return response.status_code == 200
    except Exception:
        return False
```

## Next Steps

- **[Development Guide](../development/contributing.md)** - Contribute to the project
- **[Testing Guide](../development/testing.md)** - Run and write tests
- **[Troubleshooting](../troubleshooting.md)** - Resolve common issues
