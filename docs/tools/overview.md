# Tools Overview

The LinkDing MCP Server provides 9 comprehensive tools for managing your bookmarks. Each tool is designed to work seamlessly with LLMs and follows MCP best practices.

## Available Tools

| Tool | Category | Description |
|------|----------|-------------|
| [`search_bookmarks`](#search_bookmarks) | Search | Search bookmarks with flexible filters |
| [`add_bookmark`](#add_bookmark) | Management | Add new bookmarks with metadata |
| [`get_bookmark`](#get_bookmark) | Retrieval | Get specific bookmark by ID |
| [`update_bookmark`](#update_bookmark) | Management | Update existing bookmark properties |
| [`delete_bookmark`](#delete_bookmark) | Management | Delete bookmarks permanently |
| [`archive_bookmark`](#archive_bookmark) | Organization | Archive bookmarks |
| [`unarchive_bookmark`](#unarchive_bookmark) | Organization | Unarchive bookmarks |
| [`check_url`](#check_url) | Utility | Check if URL is already bookmarked |
| [`list_tags`](#list_tags) | Tags | List all available tags |
| [`list_bookmarks_by_tag`](#list_bookmarks_by_tag) | Tags | Filter bookmarks by specific tag |

## Tool Categories

### 🔍 Search Tools
- **`search_bookmarks`**: Primary search interface with multiple filter options
- **`list_bookmarks_by_tag`**: Tag-specific filtering

### 📚 Bookmark Management
- **`add_bookmark`**: Create new bookmarks
- **`get_bookmark`**: Retrieve bookmark details
- **`update_bookmark`**: Modify existing bookmarks
- **`delete_bookmark`**: Remove bookmarks

### 📦 Organization Tools
- **`archive_bookmark`**: Archive for later reference
- **`unarchive_bookmark`**: Restore from archive

### 🏷️ Tag Management
- **`list_tags`**: Discover available tags

### 🔧 Utility Tools
- **`check_url`**: Prevent duplicates and get metadata

## Common Usage Patterns

### Research Workflow
```python
# 1. Check if already bookmarked
check_url(url="https://research-paper.com")

# 2. Add if new
add_bookmark(
    url="https://research-paper.com",
    tags=["research", "ai"],
    notes="Important findings on neural networks"
)

# 3. Find related content
search_bookmarks(tag="research")
```

### Content Organization
```python
# 1. Review unread items
search_bookmarks(unread_only=True)

# 2. Update with proper tags
update_bookmark(
    bookmark_id=123,
    tags=["tutorial", "javascript", "frontend"]
)

# 3. Archive when processed
archive_bookmark(bookmark_id=123)
```

### Discovery and Exploration
```python
# 1. See what tags you have
list_tags()

# 2. Explore a category
list_bookmarks_by_tag(tag_name="tutorials")

# 3. Search within category
search_bookmarks(tag="tutorials", query="react")
```

## Error Handling

Error handling has a deliberate layer boundary:

- `LinkDingClient` raises `LinkDingError` (including `RateLimitError`) for
  expected API, connectivity, and rate-limit failures.
- MCP tools catch those domain errors, log them, and return a stable
  `Error: <message>` string because MCP tool responses are values rather than
  Python exceptions.
- Validation and unexpected programming failures are handled at the tool
  boundary with operation-specific context.

## Response Formats

### Success Responses
Tools return structured data in JSON format:

```json
{
  "id": 123,
  "url": "https://example.com",
  "title": "Example Site",
  "description": "An example website",
  "tags": ["example", "demo"],
  "date_added": "2024-01-15T10:30:00Z"
}
```

### Error Responses
Errors are returned as descriptive strings:

```
"Error: Bookmark with ID 999 not found"
"Error: Invalid URL format"
"Error: Connection to LinkDing failed"
```

## Performance Considerations

### Pagination
- Use `limit` and `offset` parameters for large result sets
- Default limits are set to reasonable values
- Consider memory usage when requesting large datasets

### Rate Limiting
- The server respects LinkDing's rate limits
- Batch operations when possible
- Use appropriate delays for bulk operations

### Caching
- LinkDing handles caching internally
- Fresh data is always returned
- No client-side caching implemented

## Security Features

### API Token Protection
- Tokens are never logged or exposed
- Secure transmission to LinkDing API
- Environment variable isolation

### Input Validation
- URL validation for bookmark operations
- Parameter type checking
- SQL injection prevention (handled by LinkDing)

### Access Control
- Respects LinkDing user permissions
- No privilege escalation possible
- Read-only operations where appropriate

## Next Steps

Explore detailed documentation for each tool category:

- **[Search Tools](search.md)** - Advanced search and filtering
- **[Bookmark Management](bookmarks.md)** - CRUD operations
- **[Tag Management](tags.md)** - Organization and categorization

Or jump to specific integration guides:

- **[Claude Desktop](../integration/claude.md)** - Desktop integration
- **[API Reference](../api/reference.md)** - Technical details
