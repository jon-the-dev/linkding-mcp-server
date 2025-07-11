# Testing Guide

Comprehensive guide for testing the LinkDing MCP Server, including unit tests, integration tests, and testing best practices.

## Test Structure

### Test Organization

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_server.py           # Server initialization tests
├── test_tools.py            # Individual tool tests
├── test_integration.py      # Integration tests with real LinkDing
├── test_error_handling.py   # Error handling tests
└── fixtures/                # Test data fixtures
    ├── bookmarks.json
    └── responses.json
```

### Test Categories

| Category | Purpose | When to Run |
|----------|---------|-------------|
| **Unit Tests** | Test individual functions in isolation | Every commit |
| **Integration Tests** | Test with real LinkDing instance | Before releases |
| **Error Handling Tests** | Test error conditions and edge cases | Every commit |
| **Performance Tests** | Test response times and resource usage | Before releases |

## Setting Up Tests

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

### Test Configuration

Create `tests/conftest.py`:

```python
import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    original_env = {}
    test_env = {
        "LINKDING_URL": "http://test.linkding.com",
        "LINKDING_API_TOKEN": "test_token_12345",
        "DEBUG": "false"
    }
    
    # Store original values
    for key in test_env:
        original_env[key] = os.environ.get(key)
        os.environ[key] = test_env[key]
    
    yield test_env
    
    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

@pytest.fixture
def sample_bookmark():
    """Sample bookmark data for testing"""
    return {
        "id": 123,
        "url": "https://example.com",
        "title": "Example Site",
        "description": "An example website for testing",
        "notes": "Test notes here",
        "tag_names": ["test", "example", "demo"],
        "is_archived": False,
        "unread": False,
        "shared": False,
        "date_added": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-16T14:20:00Z",
        "favicon_url": "https://example.com/favicon.ico",
        "preview_image_url": None,
        "web_archive_snapshot_url": None
    }

@pytest.fixture
def sample_search_response(sample_bookmark):
    """Sample search response from LinkDing API"""
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [sample_bookmark]
    }

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing"""
    client = AsyncMock()
    return client

@pytest.fixture
def load_fixture():
    """Helper to load JSON fixtures"""
    def _load_fixture(filename):
        fixture_path = FIXTURES_DIR / filename
        with open(fixture_path, 'r') as f:
            return json.load(f)
    return _load_fixture
```

## Unit Tests

### Testing Search Tools

```python
# tests/test_tools.py
import pytest
import json
from unittest.mock import patch, AsyncMock
import httpx

from linkding_server import search_bookmarks, add_bookmark, get_bookmark

class TestSearchBookmarks:
    @pytest.mark.asyncio
    async def test_search_success(self, mock_env, sample_search_response):
        """Test successful bookmark search"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_search_response
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await search_bookmarks(query="test", limit=10)
            data = json.loads(result)
            
            assert data["count"] == 1
            assert len(data["results"]) == 1
            assert data["results"][0]["title"] == "Example Site"
            
            # Verify API call
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "q=test" in str(call_args)
            assert "limit=10" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_search_with_tag_filter(self, mock_env, sample_search_response):
        """Test search with tag filtering"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_search_response
            mock_get.return_value = mock_response
            
            result = await search_bookmarks(tag="python", limit=20)
            data = json.loads(result)
            
            assert data["count"] == 1
            
            # Verify tag parameter was passed
            call_args = mock_get.call_args
            assert "tag=python" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_search_archived_bookmarks(self, mock_env, sample_search_response):
        """Test searching archived bookmarks"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_search_response
            mock_get.return_value = mock_response
            
            result = await search_bookmarks(archived=True)
            
            # Verify archived parameter
            call_args = mock_get.call_args
            assert "archived=True" in str(call_args) or "archived=true" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_search_empty_results(self, mock_env):
        """Test search with no results"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "count": 0,
                "results": []
            }
            mock_get.return_value = mock_response
            
            result = await search_bookmarks(query="nonexistent")
            data = json.loads(result)
            
            assert data["count"] == 0
            assert len(data["results"]) == 0

class TestAddBookmark:
    @pytest.mark.asyncio
    async def test_add_bookmark_success(self, mock_env, sample_bookmark):
        """Test successful bookmark addition"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_bookmark
            mock_response.status_code = 201
            mock_post.return_value = mock_response
            
            result = await add_bookmark(
                url="https://example.com",
                title="Test Bookmark",
                tags=["test", "demo"]
            )
            
            data = json.loads(result)
            assert data["url"] == "https://example.com"
            assert data["title"] == "Example Site"
            
            # Verify POST data
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            post_data = call_args[1]['json']
            assert post_data['url'] == "https://example.com"
            assert post_data['title'] == "Test Bookmark"
            assert post_data['tag_names'] == ["test", "demo"]
    
    @pytest.mark.asyncio
    async def test_add_bookmark_minimal(self, mock_env, sample_bookmark):
        """Test adding bookmark with minimal data"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_bookmark
            mock_post.return_value = mock_response
            
            result = await add_bookmark(url="https://minimal.com")
            
            # Should succeed with just URL
            data = json.loads(result)
            assert "url" in data
            
            # Verify minimal POST data
            call_args = mock_post.call_args
            post_data = call_args[1]['json']
            assert post_data['url'] == "https://minimal.com"
            assert post_data.get('tag_names', []) == []

class TestGetBookmark:
    @pytest.mark.asyncio
    async def test_get_bookmark_success(self, mock_env, sample_bookmark):
        """Test successful bookmark retrieval"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_bookmark
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await get_bookmark(bookmark_id=123)
            data = json.loads(result)
            
            assert data["id"] == 123
            assert data["title"] == "Example Site"
            
            # Verify correct endpoint called
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "/api/bookmarks/123/" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_get_bookmark_not_found(self, mock_env):
        """Test getting non-existent bookmark"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_get.side_effect = httpx.HTTPStatusError(
                "Not Found",
                request=AsyncMock(),
                response=mock_response
            )
            
            result = await get_bookmark(bookmark_id=999)
            
            assert "Error:" in result
            assert "not found" in result.lower()
```

### Testing Error Handling

```python
# tests/test_error_handling.py
import pytest
import httpx
from unittest.mock import patch, AsyncMock

from linkding_server import search_bookmarks, add_bookmark

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_connection_error(self, mock_env):
        """Test handling of connection errors"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            
            result = await search_bookmarks(query="test")
            
            assert "Error:" in result
            assert "Connection failed" in result or "connection" in result.lower()
    
    @pytest.mark.asyncio
    async def test_timeout_error(self, mock_env):
        """Test handling of timeout errors"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")
            
            result = await search_bookmarks(query="test")
            
            assert "Error:" in result
            assert "timeout" in result.lower()
    
    @pytest.mark.asyncio
    async def test_unauthorized_error(self, mock_env):
        """Test handling of 401 Unauthorized"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_get.side_effect = httpx.HTTPStatusError(
                "Unauthorized",
                request=AsyncMock(),
                response=mock_response
            )
            
            result = await search_bookmarks(query="test")
            
            assert "Error:" in result
            assert "unauthorized" in result.lower() or "token" in result.lower()
    
    @pytest.mark.asyncio
    async def test_server_error(self, mock_env):
        """Test handling of 500 server errors"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_get.side_effect = httpx.HTTPStatusError(
                "Internal Server Error",
                request=AsyncMock(),
                response=mock_response
            )
            
            result = await search_bookmarks(query="test")
            
            assert "Error:" in result
            assert "500" in result or "server error" in result.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self, mock_env):
        """Test handling of invalid JSON responses"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await search_bookmarks(query="test")
            
            assert "Error:" in result
    
    @pytest.mark.asyncio
    async def test_add_bookmark_validation_error(self, mock_env):
        """Test bookmark addition with validation errors"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 400
            mock_response.text = "Invalid URL format"
            mock_post.side_effect = httpx.HTTPStatusError(
                "Bad Request",
                request=AsyncMock(),
                response=mock_response
            )
            
            result = await add_bookmark(url="invalid-url")
            
            assert "Error:" in result
            assert "400" in result or "bad request" in result.lower()
```

## Integration Tests

### Real LinkDing Testing

```python
# tests/test_integration.py
import pytest
import os
import json
from linkding_server import (
    search_bookmarks, add_bookmark, get_bookmark, 
    delete_bookmark, list_tags, check_url
)

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("LINKDING_API_TOKEN") or not os.getenv("LINKDING_URL"),
    reason="Integration tests require real LinkDing instance"
)
class TestIntegration:
    """
    Integration tests that run against a real LinkDing instance.
    
    Requirements:
    - LINKDING_URL environment variable set
    - LINKDING_API_TOKEN environment variable set
    - LinkDing instance running and accessible
    """
    
    @pytest.mark.asyncio
    async def test_search_real_bookmarks(self):
        """Test search against real LinkDing instance"""
        result = await search_bookmarks(query="", limit=5)
        
        # Should return valid JSON
        data = json.loads(result)
        assert "count" in data
        assert "results" in data
        assert isinstance(data["results"], list)
    
    @pytest.mark.asyncio
    async def test_list_real_tags(self):
        """Test listing tags from real instance"""
        result = await list_tags(limit=10)
        
        data = json.loads(result)
        assert "count" in data
        assert "results" in data
        assert isinstance(data["results"], list)
    
    @pytest.mark.asyncio
    async def test_check_url_real(self):
        """Test URL checking against real instance"""
        # Use a common URL that might exist
        result = await check_url(url="https://github.com")
        
        data = json.loads(result)
        assert "is_bookmarked" in data
        assert isinstance(data["is_bookmarked"], bool)
        
        if data["is_bookmarked"]:
            assert "bookmark" in data
        else:
            assert "metadata" in data
    
    @pytest.mark.asyncio
    async def test_full_bookmark_lifecycle(self):
        """Test complete bookmark lifecycle: add, get, update, delete"""
        test_url = "https://httpbin.org/json"  # Reliable test URL
        
        # 1. Check if URL already exists
        check_result = await check_url(url=test_url)
        check_data = json.loads(check_result)
        
        if check_data["is_bookmarked"]:
            # Clean up existing bookmark first
            existing_id = check_data["bookmark"]["id"]
            await delete_bookmark(bookmark_id=existing_id)
        
        # 2. Add bookmark
        add_result = await add_bookmark(
            url=test_url,
            title="Test Bookmark",
            tags=["test", "integration"],
            notes="Created during integration test"
        )
        add_data = json.loads(add_result)
        bookmark_id = add_data["id"]
        
        try:
            # 3. Get bookmark
            get_result = await get_bookmark(bookmark_id=bookmark_id)
            get_data = json.loads(get_result)
            
            assert get_data["id"] == bookmark_id
            assert get_data["url"] == test_url
            assert get_data["title"] == "Test Bookmark"
            assert "test" in get_data["tag_names"]
            assert "integration" in get_data["tag_names"]
            
            # 4. Update bookmark
            update_result = await update_bookmark(
                bookmark_id=bookmark_id,
                notes="Updated during integration test",
                tags=["test", "integration", "updated"]
            )
            update_data = json.loads(update_result)
            
            assert "updated" in update_data["tag_names"]
            assert update_data["notes"] == "Updated during integration test"
            
        finally:
            # 5. Clean up - delete bookmark
            delete_result = await delete_bookmark(bookmark_id=bookmark_id)
            assert "success" in delete_result.lower() or "deleted" in delete_result.lower()
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_tools.py

# Run specific test class
python -m pytest tests/test_tools.py::TestSearchBookmarks

# Run specific test method
python -m pytest tests/test_tools.py::TestSearchBookmarks::test_search_success
```

### Test Coverage

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
python -m pytest --cov=linkding_server

# Generate HTML coverage report
python -m pytest --cov=linkding_server --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
```

### Integration Tests

```bash
# Set up environment for integration tests
export LINKDING_URL="http://127.0.0.1:9090"
export LINKDING_API_TOKEN="your_real_token"

# Run only integration tests
python -m pytest -m integration

# Skip integration tests
python -m pytest -m "not integration"

# Run integration tests with verbose output
python -m pytest -m integration -v -s
```

### Parallel Testing

```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
python -m pytest -n auto

# Run with specific number of workers
python -m pytest -n 4
```

## Test Data and Fixtures

### Creating Test Fixtures

Create `tests/fixtures/bookmarks.json`:

```json
{
  "single_bookmark": {
    "id": 1,
    "url": "https://example.com",
    "title": "Example Site",
    "description": "An example website",
    "notes": "Test notes",
    "tag_names": ["test", "example"],
    "is_archived": false,
    "unread": false,
    "shared": false,
    "date_added": "2024-01-15T10:30:00Z",
    "date_modified": "2024-01-15T10:30:00Z"
  },
  "search_response": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "url": "https://example.com",
        "title": "Example Site",
        "tag_names": ["test"]
      },
      {
        "id": 2,
        "url": "https://test.com",
        "title": "Test Site",
        "tag_names": ["demo"]
      }
    ]
  }
}
```

### Using Fixtures in Tests

```python
def test_with_fixture(load_fixture):
    """Test using JSON fixture data"""
    bookmark_data = load_fixture("bookmarks.json")
    single_bookmark = bookmark_data["single_bookmark"]
    
    assert single_bookmark["id"] == 1
    assert single_bookmark["url"] == "https://example.com"
```

## Performance Testing

### Response Time Testing

```python
# tests/test_performance.py
import pytest
import time
import asyncio
from linkding_server import search_bookmarks

@pytest.mark.performance
class TestPerformance:
    @pytest.mark.asyncio
    async def test_search_response_time(self, mock_env, sample_search_response):
        """Test that search responds within acceptable time"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_search_response
            mock_get.return_value = mock_response
            
            start_time = time.time()
            result = await search_bookmarks(query="test")
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < 1.0  # Should respond within 1 second
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_env, sample_search_response):
        """Test handling multiple concurrent requests"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = sample_search_response
            mock_get.return_value = mock_response
            
            # Create multiple concurrent requests
            tasks = [
                search_bookmarks(query=f"test{i}")
                for i in range(10)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # All requests should complete
            assert len(results) == 10
            assert all(len(result) > 0 for result in results)
            
            # Should complete reasonably quickly
            total_time = end_time - start_time
            assert total_time < 5.0  # 10 requests in under 5 seconds
```

## Continuous Integration

### GitHub Actions Configuration

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12, 3.13]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 linkding_server.py tests/
    
    - name: Type check with mypy
      run: |
        mypy linkding_server.py
    
    - name: Test with pytest
      run: |
        python -m pytest --cov=linkding_server --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Best Practices

### Writing Good Tests

1. **Test one thing at a time:**
   ```python
   # Good: Tests one specific behavior
   async def test_search_with_limit():
       result = await search_bookmarks(limit=5)
       data = json.loads(result)
       assert len(data["results"]) <= 5
   
   # Avoid: Testing multiple behaviors
   async def test_search_everything():
       # Tests limit, query, tags, etc. all in one test
   ```

2. **Use descriptive test names:**
   ```python
   # Good: Clear what is being tested
   async def test_search_returns_empty_list_when_no_matches():
       pass
   
   # Avoid: Vague test names
   async def test_search():
       pass
   ```

3. **Arrange, Act, Assert pattern:**
   ```python
   async def test_add_bookmark_success():
       # Arrange
       url = "https://example.com"
       title = "Test Bookmark"
       
       # Act
       result = await add_bookmark(url=url, title=title)
       
       # Assert
       data = json.loads(result)
       assert data["url"] == url
       assert data["title"] == title
   ```

### Mock Best Practices

1. **Mock at the right level:**
   ```python
   # Good: Mock HTTP client
   with patch('httpx.AsyncClient.get') as mock_get:
       pass
   
   # Avoid: Mocking too high level
   with patch('linkding_server.search_bookmarks') as mock_search:
       pass
   ```

2. **Verify interactions:**
   ```python
   with patch('httpx.AsyncClient.post') as mock_post:
       await add_bookmark(url="https://test.com")
       
       # Verify the call was made correctly
       mock_post.assert_called_once()
       call_args = mock_post.call_args
       assert call_args[1]['json']['url'] == "https://test.com"
   ```

### Test Maintenance

1. **Keep tests up to date with code changes**
2. **Remove obsolete tests**
3. **Update test data when API changes**
4. **Refactor common test code into fixtures**
5. **Document complex test scenarios**

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with Python debugger
python -m pytest --pdb

# Run specific test with debugger
python -m pytest tests/test_tools.py::test_search_success --pdb

# Print output during tests
python -m pytest -s

# Verbose output with print statements
python -m pytest -v -s
```

### Test Debugging Tips

1. **Add print statements:**
   ```python
   async def test_debug_example():
       result = await search_bookmarks(query="test")
       print(f"Result: {result}")  # Will show with -s flag
       assert "test" in result
   ```

2. **Use pytest fixtures for debugging:**
   ```python
   @pytest.fixture
   def debug_mode():
       import logging
       logging.basicConfig(level=logging.DEBUG)
       yield
   ```

3. **Capture and examine mock calls:**
   ```python
   with patch('httpx.AsyncClient.get') as mock_get:
       await search_bookmarks(query="test")
       
       print(f"Mock called with: {mock_get.call_args}")
       print(f"Mock call count: {mock_get.call_count}")
   ```

## Next Steps

- **[Contributing Guide](contributing.md)** - Learn how to contribute to the project
- **[API Reference](../api/reference.md)** - Technical implementation details
- **[Troubleshooting](../troubleshooting.md)** - Debug common issues