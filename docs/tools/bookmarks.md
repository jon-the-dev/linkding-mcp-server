# Bookmark Management

Complete guide to creating, reading, updating, and deleting bookmarks with the LinkDing MCP Server.

## add_bookmark

Add new bookmarks to your LinkDing collection.

### Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `url` | string | - | ✅ | The URL to bookmark |
| `title` | string | `null` | ❌ | Custom title (auto-scraped if not provided) |
| `description` | string | `null` | ❌ | Custom description (auto-scraped if not provided) |
| `notes` | string | `null` | ❌ | Personal notes |
| `tags` | array | `null` | ❌ | List of tag names |
| `is_archived` | boolean | `false` | ❌ | Save directly to archive |
| `unread` | boolean | `false` | ❌ | Mark as unread |
| `shared` | boolean | `false` | ❌ | Share with other users |

### Basic Examples

#### Simple Bookmark
```python
# Minimal bookmark - title and description auto-scraped
add_bookmark(url="https://python.org")
```

#### Bookmark with Details
```python
add_bookmark(
    url="https://fastapi.tiangolo.com",
    title="FastAPI Documentation",
    description="Modern, fast web framework for building APIs",
    tags=["python", "api", "documentation"],
    notes="Great for building REST APIs quickly"
)
```

#### Archive Immediately
```python
add_bookmark(
    url="https://old-tutorial.com",
    tags=["tutorial", "archived"],
    is_archived=True,
    notes="Old but still useful reference"
)
```

### Advanced Usage

#### Batch Adding
```python
urls_to_add = [
    {
        "url": "https://react.dev",
        "tags": ["react", "documentation"],
        "notes": "Official React docs"
    },
    {
        "url": "https://nextjs.org",
        "tags": ["react", "nextjs", "framework"],
        "notes": "React framework for production"
    }
]

for bookmark_data in urls_to_add:
    add_bookmark(**bookmark_data)
```

#### Reading List Workflow
```python
add_bookmark(
    url="https://long-article.com",
    tags=["to-read", "article"],
    unread=True,
    notes="Recommended by colleague"
)
```

## get_bookmark

Retrieve detailed information about a specific bookmark.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bookmark_id` | integer | ✅ | The bookmark ID |

### Examples

```python
# Get bookmark details
bookmark = get_bookmark(bookmark_id=123)

# Access bookmark properties
print(f"Title: {bookmark['title']}")
print(f"URL: {bookmark['url']}")
print(f"Tags: {bookmark['tag_names']}")
```

### Response Format

```json
{
  "id": 123,
  "url": "https://example.com",
  "title": "Example Site",
  "description": "An example website",
  "notes": "Personal notes here",
  "tag_names": ["example", "demo"],
  "date_added": "2024-01-15T10:30:00Z",
  "date_modified": "2024-01-16T14:20:00Z",
  "is_archived": false,
  "unread": false,
  "shared": false,
  "favicon_url": "https://example.com/favicon.ico",
  "preview_image_url": null,
  "web_archive_snapshot_url": null
}
```

## update_bookmark

Modify existing bookmark properties.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bookmark_id` | integer | ✅ | The bookmark ID |
| `url` | string | ❌ | New URL |
| `title` | string | ❌ | New title |
| `description` | string | ❌ | New description |
| `notes` | string | ❌ | New notes |
| `tags` | array | ❌ | New list of tag names (replaces existing) |
| `is_archived` | boolean | ❌ | Update archived status |
| `unread` | boolean | ❌ | Update unread status |
| `shared` | boolean | ❌ | Update shared status |

### Examples

#### Update Tags
```python
update_bookmark(
    bookmark_id=123,
    tags=["python", "tutorial", "advanced"]
)
```

#### Add Notes
```python
update_bookmark(
    bookmark_id=123,
    notes="Updated with new insights from 2024 conference"
)
```

#### Mark as Read
```python
update_bookmark(
    bookmark_id=123,
    unread=False,
    notes="Finished reading - great resource!"
)
```

#### Complete Update
```python
update_bookmark(
    bookmark_id=123,
    title="Updated Title",
    description="Updated description with more details",
    tags=["updated", "comprehensive"],
    notes="Completely revised bookmark",
    unread=False
)
```

### Partial Updates

You only need to specify the fields you want to change:

```python
# Only update tags
update_bookmark(bookmark_id=123, tags=["new-tag"])

# Only add notes
update_bookmark(bookmark_id=123, notes="Important note")

# Only change archived status
update_bookmark(bookmark_id=123, is_archived=True)
```

## delete_bookmark

Permanently remove a bookmark from your collection.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bookmark_id` | integer | ✅ | The bookmark ID |

### Examples

```python
# Delete a bookmark
delete_bookmark(bookmark_id=123)

# Delete with confirmation workflow
bookmark = get_bookmark(bookmark_id=123)
print(f"About to delete: {bookmark['title']}")
confirm = input("Are you sure? (y/N): ")
if confirm.lower() == 'y':
    delete_bookmark(bookmark_id=123)
```

!!! warning "Permanent Deletion"
    Deleted bookmarks cannot be recovered. Consider archiving instead of deleting if you might need the bookmark later.

## archive_bookmark / unarchive_bookmark

Organize bookmarks by archiving them for later reference.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bookmark_id` | integer | ✅ | The bookmark ID |

### Examples

#### Archive Bookmark
```python
# Archive a bookmark
archive_bookmark(bookmark_id=123)

# Archive with workflow
bookmark = get_bookmark(bookmark_id=123)
if bookmark['unread'] == False:  # Only archive if read
    archive_bookmark(bookmark_id=123)
```

#### Unarchive Bookmark
```python
# Bring bookmark back to active collection
unarchive_bookmark(bookmark_id=123)
```

### Archive Workflows

#### Batch Archive Old Bookmarks
```python
# Find old bookmarks to archive
old_bookmarks = search_bookmarks(
    query="",
    archived=False,
    limit=100
)

for bookmark in old_bookmarks:
    # Archive if older than 6 months and read
    if not bookmark['unread']:
        archive_bookmark(bookmark_id=bookmark['id'])
```

#### Seasonal Archive
```python
# Archive bookmarks with specific tags
tutorial_bookmarks = search_bookmarks(tag="old-tutorial")
for bookmark in tutorial_bookmarks:
    archive_bookmark(bookmark_id=bookmark['id'])
```

## check_url

Check if a URL is already bookmarked and get metadata.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✅ | The URL to check |

### Examples

```python
# Check if URL is already bookmarked
result = check_url(url="https://python.org")

if result['is_bookmarked']:
    print(f"Already bookmarked: {result['bookmark']['title']}")
else:
    print("Not bookmarked yet")
    print(f"Suggested title: {result['metadata']['title']}")
```

### Response Format

```json
{
  "is_bookmarked": true,
  "bookmark": {
    "id": 123,
    "title": "Python.org",
    "url": "https://python.org",
    "tag_names": ["python", "documentation"]
  },
  "metadata": {
    "title": "Welcome to Python.org",
    "description": "The official home of the Python Programming Language",
    "auto_tags": ["programming", "python"]
  }
}
```

### Use Cases

#### Prevent Duplicates
```python
def smart_add_bookmark(url, **kwargs):
    result = check_url(url=url)
    
    if result['is_bookmarked']:
        print(f"URL already bookmarked: {result['bookmark']['title']}")
        return result['bookmark']
    else:
        # Use scraped metadata if not provided
        if 'title' not in kwargs and result['metadata']['title']:
            kwargs['title'] = result['metadata']['title']
        if 'description' not in kwargs and result['metadata']['description']:
            kwargs['description'] = result['metadata']['description']
            
        return add_bookmark(url=url, **kwargs)
```

#### Bulk Import with Deduplication
```python
urls_to_import = [
    "https://python.org",
    "https://fastapi.tiangolo.com",
    "https://react.dev"
]

for url in urls_to_import:
    result = check_url(url=url)
    if not result['is_bookmarked']:
        add_bookmark(
            url=url,
            title=result['metadata']['title'],
            description=result['metadata']['description']
        )
    else:
        print(f"Skipping duplicate: {url}")
```

## Common Workflows

### Research Session Workflow

```python
def research_workflow(urls, topic_tag):
    """Add multiple research URLs with consistent tagging"""
    added_bookmarks = []
    
    for url in urls:
        # Check if already exists
        result = check_url(url=url)
        
        if not result['is_bookmarked']:
            bookmark = add_bookmark(
                url=url,
                title=result['metadata']['title'],
                tags=[topic_tag, "research", "to-read"],
                unread=True,
                notes=f"Added during {topic_tag} research session"
            )
            added_bookmarks.append(bookmark)
        else:
            # Update existing bookmark with research tag
            existing = result['bookmark']
            current_tags = existing['tag_names']
            if topic_tag not in current_tags:
                current_tags.append(topic_tag)
                update_bookmark(
                    bookmark_id=existing['id'],
                    tags=current_tags
                )
    
    return added_bookmarks
```

### Reading List Management

```python
def manage_reading_list():
    """Process unread bookmarks"""
    unread = search_bookmarks(unread_only=True, limit=20)
    
    for bookmark in unread:
        print(f"Title: {bookmark['title']}")
        print(f"URL: {bookmark['url']}")
        
        action = input("(r)ead, (a)rchive, (d)elete, (s)kip: ")
        
        if action == 'r':
            update_bookmark(
                bookmark_id=bookmark['id'],
                unread=False,
                notes="Read and processed"
            )
        elif action == 'a':
            archive_bookmark(bookmark_id=bookmark['id'])
        elif action == 'd':
            delete_bookmark(bookmark_id=bookmark['id'])
```

### Bookmark Cleanup

```python
def cleanup_bookmarks():
    """Clean up and organize bookmarks"""
    
    # Find bookmarks without tags
    all_bookmarks = search_bookmarks(query="", limit=100)
    untagged = [b for b in all_bookmarks if not b['tag_names']]
    
    for bookmark in untagged:
        print(f"Untagged: {bookmark['title']}")
        tags = input("Enter tags (comma-separated): ").split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        if tags:
            update_bookmark(
                bookmark_id=bookmark['id'],
                tags=tags
            )
```

## Error Handling

### Common Errors

```python
try:
    bookmark = get_bookmark(bookmark_id=999)
except Exception as e:
    if "not found" in str(e):
        print("Bookmark doesn't exist")
    else:
        print(f"Error: {e}")

try:
    add_bookmark(url="invalid-url")
except Exception as e:
    if "Invalid URL" in str(e):
        print("Please provide a valid URL")
    else:
        print(f"Error: {e}")
```

### Validation

```python
def safe_add_bookmark(url, **kwargs):
    """Add bookmark with validation"""
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        return {"error": "URL must start with http:// or https://"}
    
    # Check for duplicates
    result = check_url(url=url)
    if result['is_bookmarked']:
        return {"error": "URL already bookmarked", "existing": result['bookmark']}
    
    # Add bookmark
    try:
        return add_bookmark(url=url, **kwargs)
    except Exception as e:
        return {"error": str(e)}
```

## Next Steps

- **[Tag Management](tags.md)** - Organize bookmarks with tags
- **[Search Tools](search.md)** - Find bookmarks efficiently
- **[Integration Guide](../integration/claude.md)** - Use with Claude Desktop