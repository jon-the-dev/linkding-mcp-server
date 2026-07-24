# Contributing

Thank you for your interest in contributing to the LinkDing MCP Server! This guide will help you get started with development and contributing to the project.

## Getting Started

### Development Environment Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/linkding-mcp-server.git
   cd linkding-mcp-server
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up environment:**
   ```bash
   cp .env.sample .env
   # Edit .env with your LinkDing configuration
   ```

5. **Run tests:**
   ```bash
   python -m pytest
   ```

### Development Dependencies

Create `requirements-dev.txt` for development tools:

```txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0
```

## Project Structure

```
linkding-mcp-server/
├── linkding_server.py      # Main server implementation
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── .env.sample            # Environment template
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
├── tests/                 # Test files
│   ├── __init__.py
│   ├── test_server.py     # Server tests
│   ├── test_tools.py      # Tool tests
│   └── conftest.py        # Test configuration
├── docs/                  # Documentation
│   ├── mkdocs.yml         # MkDocs configuration
│   └── ...                # Documentation files
└── examples/              # Usage examples
    ├── basic_usage.py
    └── advanced_workflows.py
```

## Code Style and Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **String quotes**: Double quotes preferred
- **Import order**: Standard library, third-party, local imports
- **Type hints**: Required for all public functions

### Code Formatting

Use Black for code formatting:

```bash
# Format all Python files
black .

# Check formatting
black --check .
```

### Linting

Use flake8 for linting:

```bash
# Run linter
flake8 linkding_server.py tests/

# Configuration in setup.cfg or .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

### Type Checking

Use mypy for type checking:

```bash
# Run type checker
mypy linkding_server.py

# Configuration in mypy.ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

## Development Workflow

### Pre-commit Hooks

Set up pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Branch Strategy

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Add: descriptive commit message"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```
feat(tools): add bookmark export functionality
fix(search): handle empty query parameters correctly
docs(api): update tool parameter documentation
```

## Adding New Features

### Adding New Tools

1. **Define the tool function:**
   ```python
   @mcp.tool()
   async def new_tool_name(
       param1: str,
       param2: Optional[int] = None
   ) -> str:
       """
       Tool description for MCP clients.
       
       Args:
           param1: Description of parameter 1
           param2: Description of parameter 2
           
       Returns:
           JSON string with results
       """
       try:
           # Implementation here
           result = await some_api_call(param1, param2)
           return json.dumps(result)
       except LinkDingError as error:
           logger.error("new_tool_failed", error=str(error))
           return _format_client_error(error)
       except Exception as error:
           logger.error("unexpected_error", error=str(error))
           return f"Error running new tool: {error}"
   ```

2. **Add comprehensive docstring:**
   - Clear description of what the tool does
   - Parameter descriptions with types
   - Return value description
   - Usage examples in docstring

3. **Add error handling:**
   - Let client methods raise `LinkDingError`
   - Translate `LinkDingError` with `_format_client_error` at the MCP boundary
   - Reserve broad exception handling for unexpected tool-boundary failures
   - Log errors for debugging

4. **Write tests:**
   ```python
   @pytest.mark.asyncio
   async def test_new_tool_name():
       # Test successful case
       result = await new_tool_name("test_param")
       assert "expected_value" in result
       
       # Test error case
       result = await new_tool_name("")
       assert "Error:" in result
   ```

### Adding New Data Models

1. **Define Pydantic model:**
   ```python
   class NewModel(BaseModel):
       """Description of the model"""
       id: int
       name: str
       optional_field: Optional[str] = None
       created_at: datetime
       
       class Config:
           # Configuration options
           json_encoders = {
               datetime: lambda v: v.isoformat()
           }
   ```

2. **Add validation:**
   ```python
   @validator('name')
   def validate_name(cls, v):
       if not v or len(v.strip()) == 0:
           raise ValueError('Name cannot be empty')
       return v.strip()
   ```

## Testing

### Test Structure

```python
# tests/test_tools.py
import pytest
from unittest.mock import AsyncMock, patch
import json

from linkding_server import search_bookmarks, add_bookmark

class TestSearchBookmarks:
    @pytest.mark.asyncio
    async def test_search_success(self):
        """Test successful bookmark search"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "count": 1,
                "results": [{"id": 1, "title": "Test", "url": "https://test.com"}]
            }
            mock_get.return_value = mock_response
            
            result = await search_bookmarks(query="test")
            data = json.loads(result)
            
            assert data["count"] == 1
            assert len(data["results"]) == 1
            assert data["results"][0]["title"] == "Test"
    
    @pytest.mark.asyncio
    async def test_search_error(self):
        """Test search with API error"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "Not found", request=None, response=AsyncMock(status_code=404)
            )
            
            result = await search_bookmarks(query="test")
            assert "Error:" in result
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=linkding_server

# Run specific test file
python -m pytest tests/test_tools.py

# Run specific test
python -m pytest tests/test_tools.py::TestSearchBookmarks::test_search_success

# Run with verbose output
python -m pytest -v

# Run tests matching pattern
python -m pytest -k "search"
```

### Test Configuration

Create `tests/conftest.py`:

```python
import pytest
import os
from unittest.mock import AsyncMock

@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    os.environ["LINKDING_URL"] = "http://test.example.com"
    os.environ["LINKDING_API_TOKEN"] = "test_token"
    os.environ["DEBUG"] = "false"
    yield
    # Cleanup
    for key in ["LINKDING_URL", "LINKDING_API_TOKEN", "DEBUG"]:
        os.environ.pop(key, None)

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing"""
    client = AsyncMock()
    return client

@pytest.fixture
def sample_bookmark():
    """Sample bookmark data for testing"""
    return {
        "id": 1,
        "url": "https://example.com",
        "title": "Example Site",
        "description": "An example website",
        "notes": "Test notes",
        "tag_names": ["test", "example"],
        "is_archived": False,
        "unread": False,
        "shared": False,
        "date_added": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z"
    }
```

### Integration Tests

Create tests that work with a real LinkDing instance:

```python
# tests/test_integration.py
import pytest
import os

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("LINKDING_API_TOKEN"),
    reason="Integration tests require real LinkDing instance"
)
class TestIntegration:
    @pytest.mark.asyncio
    async def test_real_search(self):
        """Test search against real LinkDing instance"""
        result = await search_bookmarks(query="", limit=1)
        assert isinstance(result, str)
        
        # Should be valid JSON
        data = json.loads(result)
        assert "count" in data
        assert "results" in data
```

Run integration tests:

```bash
# Run only integration tests
python -m pytest -m integration

# Skip integration tests
python -m pytest -m "not integration"
```

## Documentation

### Code Documentation

1. **Docstrings for all public functions:**
   ```python
   async def search_bookmarks(
       query: str = "",
       tag: Optional[str] = None,
       limit: int = 100
   ) -> str:
       """
       Search for bookmarks with flexible filtering options.
       
       This tool searches through your LinkDing bookmarks using various
       filters including text search, tag filtering, and status filters.
       
       Args:
           query: Search phrase to match against title, description, notes, and URL.
                 Empty string returns all bookmarks.
           tag: Filter results to bookmarks with this specific tag.
           limit: Maximum number of bookmarks to return (default: 100).
           
       Returns:
           JSON string containing search results with the following structure:
           {
               "count": total_number_of_matches,
               "results": [list_of_bookmark_objects]
           }
           
       Raises:
           HTTPError: If LinkDing API request fails.
           
       Example:
           >>> result = await search_bookmarks(query="python", limit=10)
           >>> data = json.loads(result)
           >>> print(f"Found {data['count']} Python bookmarks")
       """
   ```

2. **Type hints for all parameters and return values**

3. **Inline comments for complex logic:**
   ```python
   # Convert tag list to comma-separated string for LinkDing API
   tag_string = ",".join(tags) if tags else ""
   
   # LinkDing expects 'true'/'false' strings for boolean parameters
   archived_param = "true" if is_archived else "false"
   ```

### MkDocs Documentation

Update documentation when adding features:

1. **Update tool reference:**
   - Add new tools to `docs/tools/overview.md`
   - Create detailed documentation in appropriate tool category files

2. **Update API reference:**
   - Add function signatures to `docs/api/reference.md`
   - Include parameter descriptions and examples

3. **Update integration guides:**
   - Add usage examples to integration documentation
   - Update configuration examples if needed

### README Updates

Keep the main README.md current:
- Update feature lists
- Add new tool descriptions
- Update examples
- Keep installation instructions current

## Performance Considerations

### Async Best Practices

1. **Use async/await properly:**
   ```python
   # Good: Proper async usage
   async def fetch_bookmarks():
       async with httpx.AsyncClient() as client:
           response = await client.get(url)
           return response.json()
   
   # Avoid: Blocking calls in async functions
   async def bad_fetch():
       response = requests.get(url)  # Blocks event loop
       return response.json()
   ```

2. **Handle connection pooling:**
   ```python
   # Reuse client instance
   client = httpx.AsyncClient()
   
   # Close properly
   async def cleanup():
       await client.aclose()
   ```

### Memory Management

1. **Use generators for large datasets:**
   ```python
   async def get_all_bookmarks():
       offset = 0
       limit = 100
       
       while True:
           batch = await search_bookmarks(limit=limit, offset=offset)
           if not batch:
               break
           
           for bookmark in batch:
               yield bookmark
           
           offset += limit
   ```

2. **Avoid loading large datasets into memory:**
   ```python
   # Good: Process in batches
   async def process_bookmarks():
       async for bookmark in get_all_bookmarks():
           await process_single_bookmark(bookmark)
   
   # Avoid: Loading everything at once
   all_bookmarks = await get_all_bookmarks()  # Could use lots of memory
   ```

## Security Considerations

### Input Validation

1. **Validate all inputs:**
   ```python
   def validate_bookmark_id(bookmark_id: int) -> int:
       if not isinstance(bookmark_id, int) or bookmark_id <= 0:
           raise ValueError("Bookmark ID must be a positive integer")
       return bookmark_id
   
   def validate_url(url: str) -> str:
       from urllib.parse import urlparse
       parsed = urlparse(url)
       if not parsed.scheme or not parsed.netloc:
           raise ValueError("Invalid URL format")
       return url
   ```

2. **Sanitize outputs:**
   ```python
   def safe_json_response(data: dict) -> str:
       """Safely serialize data to JSON"""
       try:
           return json.dumps(data, ensure_ascii=False, indent=2)
       except (TypeError, ValueError) as e:
           logger.error(f"JSON serialization error: {e}")
           return json.dumps({"error": "Failed to serialize response"})
   ```

### Logging Security

1. **Never log sensitive data:**
   ```python
   # Good: Redact sensitive information
   def log_request(url: str, headers: dict):
       safe_headers = headers.copy()
       if "Authorization" in safe_headers:
           safe_headers["Authorization"] = "[REDACTED]"
       logger.debug(f"Request to {url} with headers {safe_headers}")
   
   # Avoid: Logging tokens
   logger.debug(f"Using token: {api_token}")  # Don't do this
   ```

## Release Process

### Version Management

1. **Update version numbers:**
   - Update version in `linkding_server.py`
   - Update version in documentation
   - Create git tag

2. **Update changelog:**
   - Document new features
   - List bug fixes
   - Note breaking changes

### Testing Before Release

1. **Run full test suite:**
   ```bash
   python -m pytest
   python -m pytest -m integration  # If integration tests available
   ```

2. **Test with real LinkDing instance:**
   ```bash
   python health_check.py
   python linkding_server.py  # Manual testing
   ```

3. **Test integrations:**
   - Claude Desktop integration
   - FastMCP CLI usage
   - HTTP transport mode

### Creating Releases

1. **Create release branch:**
   ```bash
   git checkout -b release/v1.1.0
   ```

2. **Update version and documentation:**
   ```bash
   # Update version numbers
   # Update CHANGELOG.md
   # Update README.md if needed
   ```

3. **Create pull request and merge**

4. **Tag release:**
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

## Getting Help

### Development Questions

- **GitHub Discussions**: For general development questions
- **GitHub Issues**: For bug reports and feature requests
- **Code Review**: Submit PRs for feedback

### Resources

- **FastMCP Documentation**: Framework-specific guidance
- **LinkDing API Documentation**: API reference
- **MCP Specification**: Protocol details
- **Python AsyncIO**: Async programming patterns

## Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **CHANGELOG.md**: Release notes
- **GitHub**: Contributor graphs and statistics

Thank you for contributing to the LinkDing MCP Server! 🚀
