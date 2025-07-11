# Search Tools

The LinkDing MCP Server provides powerful search capabilities to help you find bookmarks quickly and efficiently.

## search_bookmarks

The primary search tool with flexible filtering options.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | `""` | Search phrase for title, description, notes, URL |
| `tag` | string | `null` | Filter by specific tag name |
| `limit` | integer | `100` | Maximum results to return |
| `offset` | integer | `0` | Results to skip for pagination |
| `archived` | boolean | `false` | Search archived bookmarks instead |
| `unread_only` | boolean | `false` | Only return unread bookmarks |

### Basic Search Examples

#### Text Search
```python
# Search for bookmarks containing "python"
search_bookmarks(query="python")

# Search for specific phrases
search_bookmarks(query="machine learning tutorial")

# Search in URLs
search_bookmarks(query="github.com")
```

#### Tag-Based Search
```python
# Find bookmarks with "tutorial" tag
search_bookmarks(tag="tutorial")

# Combine tag and text search
search_bookmarks(tag="python", query="flask")
```

#### Status-Based Search
```python
# Find unread bookmarks
search_bookmarks(unread_only=True)

# Search archived bookmarks
search_bookmarks(archived=True)

# Find unread items with specific tag
search_bookmarks(tag="to-read", unread_only=True)
```

### Advanced Search Patterns

#### Pagination
```python
# Get first 20 results
search_bookmarks(query="javascript", limit=20)

# Get next 20 results
search_bookmarks(query="javascript", limit=20, offset=20)

# Get all results in batches
def get_all_bookmarks(query):
    all_bookmarks = []
    offset = 0
    limit = 50
    
    while True:
        batch = search_bookmarks(
            query=query, 
            limit=limit, 
            offset=offset
        )
        if not batch:
            break
        all_bookmarks.extend(batch)
        offset += limit
    
    return all_bookmarks
```

#### Complex Filtering
```python
# Find recent tutorials you haven't read
search_bookmarks(
    tag="tutorial",
    unread_only=True,
    limit=10
)

# Search archived programming resources
search_bookmarks(
    query="programming",
    archived=True,
    limit=25
)
```

### Search Response Format

```json
{
  "count": 150,
  "next": "http://linkding/api/bookmarks/?offset=100",
  "previous": null,
  "results": [
    {
      "id": 123,
      "url": "https://example.com",
      "title": "Example Tutorial",
      "description": "A great tutorial about...",
      "notes": "Personal notes here",
      "tag_names": ["tutorial", "python"],
      "date_added": "2024-01-15T10:30:00Z",
      "date_modified": "2024-01-16T14:20:00Z",
      "is_archived": false,
      "unread": false,
      "shared": false,
      "favicon_url": "https://example.com/favicon.ico"
    }
  ]
}
```

## list_bookmarks_by_tag

Filter bookmarks by a specific tag.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tag_name` | string | required | Name of the tag to filter by |
| `limit` | integer | `100` | Maximum bookmarks to return |
| `offset` | integer | `0` | Bookmarks to skip for pagination |

### Examples

```python
# Get all tutorial bookmarks
list_bookmarks_by_tag(tag_name="tutorial")

# Get first 10 Python bookmarks
list_bookmarks_by_tag(tag_name="python", limit=10)

# Paginate through JavaScript bookmarks
list_bookmarks_by_tag(tag_name="javascript", limit=20, offset=40)
```

### Use Cases

#### Content Discovery
```python
# Explore what you've saved about React
react_bookmarks = list_bookmarks_by_tag(tag_name="react")

# Find all your reference materials
references = list_bookmarks_by_tag(tag_name="reference")
```

#### Project Organization
```python
# Get all bookmarks for a specific project
project_bookmarks = list_bookmarks_by_tag(tag_name="project-alpha")

# Find research materials
research = list_bookmarks_by_tag(tag_name="research")
```

## Search Best Practices

### Effective Query Construction

#### Use Specific Terms
```python
# Good: Specific and targeted
search_bookmarks(query="react hooks tutorial")

# Less effective: Too broad
search_bookmarks(query="programming")
```

#### Combine Filters
```python
# Find unread Python tutorials
search_bookmarks(
    query="python",
    tag="tutorial",
    unread_only=True
)
```

#### Use Appropriate Limits
```python
# For quick overview
search_bookmarks(query="javascript", limit=10)

# For comprehensive search
search_bookmarks(query="javascript", limit=100)
```

### Performance Optimization

#### Batch Processing
```python
def process_all_bookmarks():
    offset = 0
    batch_size = 50
    
    while True:
        batch = search_bookmarks(limit=batch_size, offset=offset)
        if not batch:
            break
            
        # Process batch
        for bookmark in batch:
            process_bookmark(bookmark)
            
        offset += batch_size
```

#### Targeted Searches
```python
# Instead of searching everything
all_bookmarks = search_bookmarks(limit=1000)

# Search specific categories
tutorials = search_bookmarks(tag="tutorial")
references = search_bookmarks(tag="reference")
```

### Common Search Patterns

#### Daily Review Workflow
```python
# 1. Check what's new and unread
new_items = search_bookmarks(unread_only=True, limit=20)

# 2. Review by category
tutorials = search_bookmarks(tag="tutorial", unread_only=True)
news = search_bookmarks(tag="news", unread_only=True)

# 3. Find items to archive
old_read = search_bookmarks(
    query="",  # All bookmarks
    archived=False,
    limit=50
)
```

#### Research Session
```python
# 1. Find existing research on topic
existing = search_bookmarks(query="machine learning")

# 2. Check specific research tag
research_items = list_bookmarks_by_tag(tag_name="ml-research")

# 3. Find related archived materials
archived_research = search_bookmarks(
    query="machine learning",
    archived=True
)
```

#### Content Curation
```python
# 1. Find all items with specific tag
content = list_bookmarks_by_tag(tag_name="blog-posts")

# 2. Search for quality indicators
high_quality = search_bookmarks(query="comprehensive guide")

# 3. Find items to review
to_review = search_bookmarks(tag="to-review")
```

## Troubleshooting Search

### No Results Found

```python
# Check if tag exists
all_tags = list_tags()
print("Available tags:", [tag["name"] for tag in all_tags])

# Try broader search
search_bookmarks(query="")  # Get all bookmarks

# Check archived items
search_bookmarks(archived=True)
```

### Too Many Results

```python
# Use more specific queries
search_bookmarks(query="python flask tutorial")

# Add tag filters
search_bookmarks(query="python", tag="tutorial")

# Reduce limit
search_bookmarks(query="python", limit=20)
```

### Performance Issues

```python
# Use pagination instead of large limits
search_bookmarks(limit=50)  # Instead of limit=1000

# Search specific categories
search_bookmarks(tag="specific-tag")  # Instead of query=""
```

## Next Steps

- **[Bookmark Management](bookmarks.md)** - Learn about CRUD operations
- **[Tag Management](tags.md)** - Organize with tags
- **[API Reference](../api/reference.md)** - Technical details