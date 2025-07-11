# Tag Management

Tags are essential for organizing and categorizing your bookmarks. The LinkDing MCP Server provides comprehensive tag management capabilities.

## list_tags

Retrieve all available tags in your LinkDing collection.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | `100` | Maximum tags to return |
| `offset` | integer | `0` | Tags to skip for pagination |

### Examples

#### Basic Tag Listing
```python
# Get all tags
all_tags = list_tags()

# Get first 20 tags
recent_tags = list_tags(limit=20)

# Paginate through tags
page_2_tags = list_tags(limit=20, offset=20)
```

#### Tag Analysis
```python
# Get tag usage statistics
tags = list_tags()
for tag in tags:
    print(f"Tag: {tag['name']} - Used {tag['bookmark_count']} times")

# Find most popular tags
popular_tags = sorted(tags, key=lambda x: x['bookmark_count'], reverse=True)[:10]
```

### Response Format

```json
{
  "count": 45,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "python",
      "bookmark_count": 25
    },
    {
      "id": 2,
      "name": "tutorial",
      "bookmark_count": 18
    },
    {
      "id": 3,
      "name": "javascript",
      "bookmark_count": 15
    }
  ]
}
```

## list_bookmarks_by_tag

Filter bookmarks by a specific tag.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tag_name` | string | ✅ | Name of the tag to filter by |
| `limit` | integer | `100` | Maximum bookmarks to return |
| `offset` | integer | `0` | Bookmarks to skip for pagination |

### Examples

#### Basic Tag Filtering
```python
# Get all Python bookmarks
python_bookmarks = list_bookmarks_by_tag(tag_name="python")

# Get first 10 tutorial bookmarks
tutorials = list_bookmarks_by_tag(tag_name="tutorial", limit=10)
```

#### Tag-Based Workflows
```python
# Review bookmarks by category
categories = ["tutorial", "reference", "news", "tools"]

for category in categories:
    bookmarks = list_bookmarks_by_tag(tag_name=category, limit=5)
    print(f"\n{category.upper()} bookmarks:")
    for bookmark in bookmarks:
        print(f"  - {bookmark['title']}")
```

## Tag Organization Strategies

### Hierarchical Tagging

Use consistent naming conventions for related tags:

```python
# Programming languages
add_bookmark(url="...", tags=["lang-python", "tutorial"])
add_bookmark(url="...", tags=["lang-javascript", "reference"])

# Project categories
add_bookmark(url="...", tags=["project-alpha", "documentation"])
add_bookmark(url="...", tags=["project-beta", "api"])

# Content types
add_bookmark(url="...", tags=["type-tutorial", "beginner"])
add_bookmark(url="...", tags=["type-reference", "advanced"])
```

### Multi-Dimensional Tagging

Combine different tag dimensions:

```python
add_bookmark(
    url="https://fastapi-tutorial.com",
    tags=[
        "python",           # Language
        "fastapi",          # Framework
        "tutorial",         # Content type
        "api",              # Topic
        "beginner"          # Difficulty
    ]
)
```

### Temporal Tagging

Use date-based tags for time-sensitive content:

```python
add_bookmark(
    url="https://tech-news.com/article",
    tags=["news", "2024", "january", "ai"]
)

add_bookmark(
    url="https://conference-talk.com",
    tags=["conference", "2024-pycon", "machine-learning"]
)
```

## Tag Management Workflows

### Tag Cleanup and Standardization

```python
def standardize_tags():
    """Clean up and standardize tag names"""
    
    # Get all tags
    tags = list_tags()
    
    # Find similar tags that should be merged
    tag_mapping = {
        "js": "javascript",
        "py": "python",
        "ml": "machine-learning",
        "ai": "artificial-intelligence"
    }
    
    for old_tag, new_tag in tag_mapping.items():
        # Find bookmarks with old tag
        bookmarks = list_bookmarks_by_tag(tag_name=old_tag)
        
        for bookmark in bookmarks:
            # Replace old tag with new tag
            current_tags = bookmark['tag_names']
            if old_tag in current_tags:
                current_tags.remove(old_tag)
                if new_tag not in current_tags:
                    current_tags.append(new_tag)
                
                update_bookmark(
                    bookmark_id=bookmark['id'],
                    tags=current_tags
                )
```

### Tag-Based Content Review

```python
def review_by_tags():
    """Review content organized by tags"""
    
    # Get most used tags
    tags = list_tags()
    popular_tags = sorted(tags, key=lambda x: x['bookmark_count'], reverse=True)[:10]
    
    for tag in popular_tags:
        print(f"\n=== {tag['name'].upper()} ({tag['bookmark_count']} bookmarks) ===")
        
        # Get recent bookmarks with this tag
        bookmarks = list_bookmarks_by_tag(tag_name=tag['name'], limit=5)
        
        for bookmark in bookmarks:
            print(f"  📖 {bookmark['title']}")
            print(f"     {bookmark['url']}")
            if bookmark['notes']:
                print(f"     💭 {bookmark['notes']}")
```

### Project-Based Tag Management

```python
def setup_project_tags(project_name):
    """Set up consistent tagging for a new project"""
    
    base_tags = [
        f"project-{project_name}",
        f"{project_name}-docs",
        f"{project_name}-tools",
        f"{project_name}-research"
    ]
    
    return base_tags

def add_project_bookmark(url, project_name, bookmark_type, **kwargs):
    """Add bookmark with project-specific tags"""
    
    project_tags = [f"project-{project_name}", bookmark_type]
    
    # Merge with any additional tags
    if 'tags' in kwargs:
        project_tags.extend(kwargs['tags'])
        kwargs['tags'] = project_tags
    else:
        kwargs['tags'] = project_tags
    
    return add_bookmark(url=url, **kwargs)

# Usage
add_project_bookmark(
    url="https://api-docs.com",
    project_name="webapp",
    bookmark_type="documentation",
    tags=["api", "reference"]
)
```

## Advanced Tag Operations

### Tag Analytics

```python
def analyze_tags():
    """Analyze tag usage patterns"""
    
    tags = list_tags()
    
    # Tag statistics
    total_tags = len(tags)
    total_usage = sum(tag['bookmark_count'] for tag in tags)
    avg_usage = total_usage / total_tags if total_tags > 0 else 0
    
    print(f"Tag Statistics:")
    print(f"  Total tags: {total_tags}")
    print(f"  Total usage: {total_usage}")
    print(f"  Average usage per tag: {avg_usage:.1f}")
    
    # Most and least used tags
    most_used = max(tags, key=lambda x: x['bookmark_count'])
    least_used = min(tags, key=lambda x: x['bookmark_count'])
    
    print(f"\nMost used tag: {most_used['name']} ({most_used['bookmark_count']} bookmarks)")
    print(f"Least used tag: {least_used['name']} ({least_used['bookmark_count']} bookmarks)")
    
    # Unused or rarely used tags
    rarely_used = [tag for tag in tags if tag['bookmark_count'] <= 2]
    print(f"\nRarely used tags ({len(rarely_used)}): {[tag['name'] for tag in rarely_used]}")
```

### Tag-Based Bookmark Discovery

```python
def discover_related_content(tag_name):
    """Find related content based on tag co-occurrence"""
    
    # Get bookmarks with the specified tag
    bookmarks = list_bookmarks_by_tag(tag_name=tag_name)
    
    # Collect all other tags used with this tag
    related_tags = {}
    for bookmark in bookmarks:
        for tag in bookmark['tag_names']:
            if tag != tag_name:
                related_tags[tag] = related_tags.get(tag, 0) + 1
    
    # Sort by frequency
    related_sorted = sorted(related_tags.items(), key=lambda x: x[1], reverse=True)
    
    print(f"Tags commonly used with '{tag_name}':")
    for tag, count in related_sorted[:10]:
        print(f"  {tag}: {count} times")
    
    return related_sorted

# Usage
discover_related_content("python")
```

### Bulk Tag Operations

```python
def bulk_tag_update(search_query, new_tags):
    """Add tags to multiple bookmarks matching a search"""
    
    bookmarks = search_bookmarks(query=search_query, limit=100)
    
    for bookmark in bookmarks:
        current_tags = bookmark['tag_names']
        
        # Add new tags if not already present
        updated_tags = current_tags.copy()
        for tag in new_tags:
            if tag not in updated_tags:
                updated_tags.append(tag)
        
        # Update if tags changed
        if updated_tags != current_tags:
            update_bookmark(
                bookmark_id=bookmark['id'],
                tags=updated_tags
            )
            print(f"Updated tags for: {bookmark['title']}")

# Usage: Add "python" tag to all Flask-related bookmarks
bulk_tag_update("flask", ["python", "web-framework"])
```

## Tag Best Practices

### Naming Conventions

#### Use Consistent Formats
```python
# Good: Consistent kebab-case
tags = ["machine-learning", "web-development", "data-science"]

# Avoid: Mixed formats
tags = ["machine_learning", "WebDevelopment", "data science"]
```

#### Use Descriptive Names
```python
# Good: Clear and descriptive
tags = ["tutorial-beginner", "reference-api", "news-2024"]

# Avoid: Vague or cryptic
tags = ["tut", "ref", "misc"]
```

#### Create Tag Hierarchies
```python
# Language tags
tags = ["lang-python", "lang-javascript", "lang-rust"]

# Framework tags
tags = ["framework-react", "framework-django", "framework-fastapi"]

# Content type tags
tags = ["type-tutorial", "type-documentation", "type-news"]
```

### Tag Maintenance

#### Regular Tag Audits
```python
def audit_tags():
    """Perform regular tag maintenance"""
    
    tags = list_tags()
    
    # Find tags with only one bookmark
    single_use_tags = [tag for tag in tags if tag['bookmark_count'] == 1]
    print(f"Single-use tags: {len(single_use_tags)}")
    
    # Find potential duplicates (similar names)
    potential_duplicates = []
    for i, tag1 in enumerate(tags):
        for tag2 in tags[i+1:]:
            if tag1['name'].lower().replace('-', '').replace('_', '') == \
               tag2['name'].lower().replace('-', '').replace('_', ''):
                potential_duplicates.append((tag1['name'], tag2['name']))
    
    if potential_duplicates:
        print("Potential duplicate tags:")
        for tag1, tag2 in potential_duplicates:
            print(f"  {tag1} <-> {tag2}")
```

#### Tag Consolidation
```python
def consolidate_tags(old_tags, new_tag):
    """Merge multiple tags into one"""
    
    all_bookmarks = []
    
    # Collect all bookmarks with old tags
    for old_tag in old_tags:
        bookmarks = list_bookmarks_by_tag(tag_name=old_tag)
        all_bookmarks.extend(bookmarks)
    
    # Remove duplicates
    unique_bookmarks = {b['id']: b for b in all_bookmarks}.values()
    
    # Update each bookmark
    for bookmark in unique_bookmarks:
        current_tags = bookmark['tag_names']
        
        # Remove old tags and add new tag
        updated_tags = [tag for tag in current_tags if tag not in old_tags]
        if new_tag not in updated_tags:
            updated_tags.append(new_tag)
        
        update_bookmark(
            bookmark_id=bookmark['id'],
            tags=updated_tags
        )

# Usage: Consolidate similar tags
consolidate_tags(["js", "javascript", "JS"], "javascript")
```

## Integration with Search

### Tag-Enhanced Search
```python
def smart_search(query, suggested_tags=None):
    """Search with automatic tag suggestions"""
    
    # Basic search
    results = search_bookmarks(query=query, limit=20)
    
    # If few results, try tag-based search
    if len(results) < 5 and suggested_tags:
        for tag in suggested_tags:
            tag_results = search_bookmarks(tag=tag, query=query)
            results.extend(tag_results)
    
    return results

# Usage
results = smart_search("api", suggested_tags=["python", "javascript", "documentation"])
```

### Tag-Based Content Curation
```python
def curate_learning_path(topic_tags):
    """Create a learning path based on tags"""
    
    learning_path = []
    
    for tag in topic_tags:
        # Get beginner content first
        beginner = search_bookmarks(tag=tag, query="beginner tutorial")
        
        # Then intermediate content
        intermediate = search_bookmarks(tag=tag, query="intermediate guide")
        
        # Finally advanced content
        advanced = search_bookmarks(tag=tag, query="advanced reference")
        
        learning_path.append({
            "topic": tag,
            "beginner": beginner[:3],
            "intermediate": intermediate[:3],
            "advanced": advanced[:3]
        })
    
    return learning_path

# Usage
path = curate_learning_path(["python", "machine-learning", "data-science"])
```

## Next Steps

- **[Search Tools](search.md)** - Use tags in advanced searches
- **[Bookmark Management](bookmarks.md)** - Apply tags when managing bookmarks
- **[API Reference](../api/reference.md)** - Technical implementation details