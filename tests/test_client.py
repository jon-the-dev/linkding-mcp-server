"""Tests for LinkDing HTTP client"""

import logging
from unittest.mock import MagicMock

import httpx
import pytest

from linkding_mcp_server.client import LinkDingClient, LinkDingError, RateLimitError, _resolve_ssl_verify
from linkding_mcp_server.config import Settings
from linkding_mcp_server.models import Bookmark, BookmarkCreate, BookmarkUpdate


@pytest.fixture
def settings():
    """Create test settings"""
    return Settings(
        linkding_url="https://linkding.example.com",
        linkding_api_token="test_token_12345",
        enable_destructive_actions=True,
        cache_ttl=0  # Disable cache for tests
    )


@pytest.fixture
def mock_response():
    """Create a mock response"""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {}
    return response


def create_mock_response(status_code: int, json_data: dict = None):
    """Helper to create mock responses"""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.text = str(json_data) if json_data else ""
    return response


def _bookmark_data(bookmark_id: int) -> dict:
    """Build a complete LinkDing bookmark response."""
    return {
        "id": bookmark_id,
        "url": f"https://example.com/{bookmark_id}",
        "title": f"Bookmark {bookmark_id}",
        "description": "",
        "notes": "",
        "is_archived": False,
        "unread": False,
        "shared": False,
        "tag_names": [],
        "date_added": "2024-01-01T00:00:00Z",
        "date_modified": "2024-01-01T00:00:00Z",
    }


class TestLinkDingClient:
    """Tests for LinkDingClient"""

    @pytest.mark.asyncio
    async def test_client_context_manager(self, settings):
        """Test client context manager"""
        async with LinkDingClient(settings) as client:
            assert client.client is not None
            assert isinstance(client.client, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_client_headers(self, settings):
        """Test that client sets correct headers"""
        async with LinkDingClient(settings) as client:
            assert "Authorization" in client.client.headers
            assert client.client.headers["Authorization"] == "Token test_token_12345"

    @pytest.mark.asyncio
    async def test_base_url_configuration(self, settings):
        """Test that base URL is configured correctly"""
        async with LinkDingClient(settings) as client:
            # httpx adds trailing slash to base_url
            assert "linkding.example.com" in str(client.client.base_url)
            assert "/api" in str(client.client.base_url)

    @pytest.mark.asyncio
    async def test_masked_token_in_logs(self, settings):
        """Test that token is masked in logs"""
        masked = settings.get_masked_token()
        assert "test" in masked
        assert "..." in masked
        # Full token should not appear
        assert "test_token_12345" not in masked

    @pytest.mark.asyncio
    async def test_retry_on_network_error(self, settings):
        """Test retry mechanism on network errors"""
        async with LinkDingClient(settings) as client:
            call_count = 0

            async def mock_request(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise httpx.NetworkError("Network error")
                return create_mock_response(200, {"results": []})

            client.client.request = mock_request

            response = await client._make_request("GET", "/test")
            assert response.status_code == 200
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, settings):
        """Test rate limit error handling"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(429)

            client.client.request = mock_request

            with pytest.raises(RateLimitError):
                await client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_get_bookmarks(self, settings):
        """Test getting bookmarks"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(200, {
                    "count": 2,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "url": "https://example.com",
                            "title": "Example",
                            "description": "",
                            "notes": "",
                            "is_archived": False,
                            "unread": False,
                            "shared": False,
                            "tag_names": ["test"],
                            "date_added": "2024-01-01T00:00:00Z",
                            "date_modified": "2024-01-01T00:00:00Z"
                        },
                        {
                            "id": 2,
                            "url": "https://test.com",
                            "title": "Test",
                            "description": "",
                            "notes": "",
                            "is_archived": False,
                            "unread": True,
                            "shared": False,
                            "tag_names": [],
                            "date_added": "2024-01-02T00:00:00Z",
                            "date_modified": "2024-01-02T00:00:00Z"
                        }
                    ]
                })

            client.client.request = mock_request

            result = await client.get_bookmarks()
            assert result.count == 2
            assert len(result.results) == 2
            assert result.results[0].title == "Example"
            assert result.results[1].unread is True

    @pytest.mark.asyncio
    async def test_create_bookmark(self, settings):
        """Test creating a bookmark"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(201, {
                    "id": 1,
                    "url": "https://example.com",
                    "title": "Example",
                    "description": "Test description",
                    "notes": "",
                    "is_archived": False,
                    "unread": False,
                    "shared": False,
                    "tag_names": ["test"],
                    "date_added": "2024-01-01T00:00:00Z",
                    "date_modified": "2024-01-01T00:00:00Z"
                })

            client.client.request = mock_request

            bookmark = BookmarkCreate(
                url="https://example.com",
                title="Example",
                description="Test description",
                tags=["test"]
            )
            result = await client.create_bookmark(bookmark)
            assert result.id == 1
            assert result.title == "Example"
            assert "test" in result.tag_names

    @pytest.mark.asyncio
    async def test_update_bookmark(self, settings):
        """Test updating a bookmark"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(200, {
                    "id": 1,
                    "url": "https://example.com",
                    "title": "Updated Title",
                    "description": "",
                    "notes": "",
                    "is_archived": False,
                    "unread": False,
                    "shared": False,
                    "tag_names": ["updated"],
                    "date_added": "2024-01-01T00:00:00Z",
                    "date_modified": "2024-01-02T00:00:00Z"
                })

            client.client.request = mock_request

            update = BookmarkUpdate(
                title="Updated Title",
                tags=["updated"]
            )
            result = await client.update_bookmark(1, update)
            assert result.title == "Updated Title"
            assert "updated" in result.tag_names

    def test_build_update_payload_includes_false_and_empty_values(self, settings):
        """The payload helper preserves explicit values while omitting only None."""
        client = LinkDingClient(settings)
        update = BookmarkUpdate(
            title="",
            description=None,
            tags=[],
            is_archived=False,
            unread=True,
            shared=False,
        )

        assert client._build_update_payload(update) == {
            "title": "",
            "tag_names": [],
            "is_archived": False,
            "unread": True,
            "shared": False,
        }

    @pytest.mark.asyncio
    async def test_paginate_results_streams_large_datasets(self, settings):
        """Pagination yields each item before requesting the following page."""
        client = LinkDingClient(settings)
        request_count = 0

        async def mock_request(method, endpoint, **kwargs):
            nonlocal request_count
            request_count += 1
            page = request_count
            next_url = (
                f"{settings.linkding_url}api/bookmarks/?page={page + 1}"
                if page < 100
                else None
            )
            return create_mock_response(
                200,
                {
                    "results": [
                        _bookmark_data((page - 1) * 100 + offset)
                        for offset in range(1, 101)
                    ],
                    "next": next_url,
                },
            )

        client._make_request = mock_request
        results = client.paginate_results("/bookmarks/", Bookmark, {})
        first = await anext(results)

        assert first.id == 1
        assert request_count == 1

        remaining_ids = [bookmark.id async for bookmark in results]
        assert remaining_ids[-1] == 10_000
        assert len(remaining_ids) == 9_999
        assert request_count == 100

    @pytest.mark.asyncio
    async def test_paginate_results_honors_result_and_page_limits(self, settings):
        """Both legacy item limits and page limits stop additional requests."""
        client = LinkDingClient(settings)
        request_count = 0

        async def mock_request(method, endpoint, **kwargs):
            nonlocal request_count
            request_count += 1
            return create_mock_response(
                200,
                {
                    "results": [_bookmark_data(request_count)],
                    "next": f"{settings.linkding_url}api/bookmarks/?page={request_count + 1}",
                },
            )

        client._make_request = mock_request
        by_page = [
            bookmark.id
            async for bookmark in client.paginate_results(
                "/bookmarks/", Bookmark, {}, max_pages=3
            )
        ]
        assert by_page == [1, 2, 3]
        assert request_count == 3

        request_count = 0
        by_result = [
            bookmark.id
            async for bookmark in client.paginate_results(
                "/bookmarks/", Bookmark, {}, max_results=2
            )
        ]
        assert by_result == [1, 2]
        assert request_count == 2

    @pytest.mark.asyncio
    async def test_delete_bookmark(self, settings):
        """Test deleting a bookmark"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(204)

            client.client.request = mock_request

            result = await client.delete_bookmark(1)
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_bookmark_not_found(self, settings):
        """Test deleting a non-existent bookmark"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(404)

            client.client.request = mock_request

            with pytest.raises(LinkDingError) as exc_info:
                await client.delete_bookmark(999)
            assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_archive_bookmark(self, settings):
        """Test archiving a bookmark"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(204)

            client.client.request = mock_request

            result = await client.archive_bookmark(1)
            assert result is True

    @pytest.mark.asyncio
    async def test_unarchive_bookmark(self, settings):
        """Test unarchiving a bookmark"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(204)

            client.client.request = mock_request

            result = await client.unarchive_bookmark(1)
            assert result is True

    @pytest.mark.asyncio
    async def test_check_url(self, settings):
        """Test checking if URL is bookmarked"""
        async with LinkDingClient(settings) as client:
            async def mock_request(*args, **kwargs):
                return create_mock_response(200, {
                    "bookmark": {
                        "id": 1,
                        "url": "https://example.com",
                        "title": "Example",
                        "description": "",
                        "notes": "",
                        "is_archived": False,
                        "unread": False,
                        "shared": False,
                        "tag_names": [],
                        "date_added": "2024-01-01T00:00:00Z",
                        "date_modified": "2024-01-01T00:00:00Z"
                    },
                    "metadata": {"title": "Example Page"},
                    "auto_tags": ["example"]
                })

            client.client.request = mock_request

            result = await client.check_url("https://example.com")
            assert result.bookmark is not None
            assert result.bookmark.id == 1
            assert "example" in result.auto_tags

    @pytest.mark.asyncio
    async def test_get_tags_with_cache(self, settings):
        """Test getting tags with caching"""
        settings_with_cache = Settings(
            linkding_url="https://linkding.example.com",
            linkding_api_token="test_token_12345",
            enable_destructive_actions=True,
            cache_ttl=300  # Enable cache
        )

        async with LinkDingClient(settings_with_cache) as client:
            call_count = 0

            async def mock_request(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                return create_mock_response(200, {
                    "count": 2,
                    "next": None,
                    "previous": None,
                    "results": [
                        {"id": 1, "name": "test", "date_added": "2024-01-01T00:00:00Z"},
                        {"id": 2, "name": "example", "date_added": "2024-01-01T00:00:00Z"}
                    ]
                })

            client.client.request = mock_request

            # First call - should hit API
            result1 = await client.get_tags()
            assert result1.count == 2

            # Second call - should use cache
            result2 = await client.get_tags()
            assert result2.count == 2

            # API should only be called once
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_error_handling_with_detail(self, settings):
        """Test error message extraction with 'detail' field"""
        async with LinkDingClient(settings) as client:
            response = create_mock_response(400, {"detail": "Invalid request parameters"})
            error = await client.handle_api_error(response)
            assert "Invalid request parameters" in error

    @pytest.mark.asyncio
    async def test_error_handling_with_nested_message(self, settings):
        """Test error message extraction with nested message"""
        async with LinkDingClient(settings) as client:
            response = create_mock_response(400, {"message": "Something went wrong"})
            error = await client.handle_api_error(response)
            assert "Something went wrong" in error

    @pytest.mark.asyncio
    async def test_client_not_initialized_error(self, settings):
        """Test error when client is used without context manager"""
        client = LinkDingClient(settings)
        with pytest.raises(LinkDingError) as exc_info:
            await client._make_request("GET", "/test")
        assert "not initialized" in str(exc_info.value)


def _make_stub_client(captured: dict):
    """Return a StubAsyncClient class that records constructor kwargs into captured."""
    class StubAsyncClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        async def aclose(self):
            pass

    return StubAsyncClient


class TestResolveSSLVerify:
    """Tests for _resolve_ssl_verify helper and httpx verify argument."""

    def test_verify_false_when_ssl_disabled(self):
        """verify_ssl=False produces verify=False."""
        settings = Settings(linkding_api_token="token", verify_ssl=False)
        assert _resolve_ssl_verify(settings) is False

    def test_verify_true_by_default(self):
        """Default settings produce verify=True."""
        settings = Settings(linkding_api_token="token")
        assert _resolve_ssl_verify(settings) is True

    def test_verify_cert_path_when_provided(self, tmp_path):
        """ssl_cert_path set produces verify=<cert_path_string>."""
        cert_file = tmp_path / "ca.pem"
        cert_file.write_text("fake ca content")

        settings = Settings(linkding_api_token="token", ssl_cert_path=str(cert_file))
        assert _resolve_ssl_verify(settings) == str(cert_file)

    def test_disabled_takes_precedence_over_cert_path(self, tmp_path):
        """verify_ssl=False takes precedence even when ssl_cert_path is set."""
        cert_file = tmp_path / "ca.pem"
        cert_file.write_text("fake ca content")

        settings = Settings(linkding_api_token="token", verify_ssl=False, ssl_cert_path=str(cert_file))
        assert _resolve_ssl_verify(settings) is False

    @pytest.mark.asyncio
    async def test_httpx_client_receives_verify_false(self, monkeypatch):
        """AsyncClient is constructed with verify=False when SSL is disabled."""
        captured: dict = {}
        monkeypatch.setattr("linkding_mcp_server.client.httpx.AsyncClient", _make_stub_client(captured))

        settings = Settings(linkding_api_token="token", verify_ssl=False)
        async with LinkDingClient(settings):
            pass
        assert captured.get("verify") is False

    @pytest.mark.asyncio
    async def test_httpx_client_receives_verify_true_default(self, monkeypatch):
        """AsyncClient is constructed with verify=True for default settings."""
        captured: dict = {}
        monkeypatch.setattr("linkding_mcp_server.client.httpx.AsyncClient", _make_stub_client(captured))

        settings = Settings(linkding_api_token="token")
        async with LinkDingClient(settings):
            pass
        assert captured.get("verify") is True

    @pytest.mark.asyncio
    async def test_httpx_client_receives_cert_path(self, monkeypatch, tmp_path):
        """AsyncClient is constructed with verify=<cert_path> for custom CA bundle."""
        cert_file = tmp_path / "ca.pem"
        cert_file.write_text("fake ca content")
        captured: dict = {}
        monkeypatch.setattr("linkding_mcp_server.client.httpx.AsyncClient", _make_stub_client(captured))

        settings = Settings(linkding_api_token="token", ssl_cert_path=str(cert_file))
        async with LinkDingClient(settings):
            pass
        assert captured.get("verify") == str(cert_file)

    def test_ssl_disabled_emits_warning(self, caplog):
        """WARNING is emitted when SSL verification is disabled."""
        settings = Settings(linkding_api_token="token", verify_ssl=False)
        with caplog.at_level(logging.WARNING, logger="linkding_mcp_server.client"):
            LinkDingClient(settings)
        assert any("DISABLED" in r.message for r in caplog.records if r.levelno == logging.WARNING)
