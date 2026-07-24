"""HTTP client for LinkDing API with retry logic and connection pooling"""

import asyncio
import logging
import time
from collections import OrderedDict
from collections.abc import AsyncIterator, Callable
from typing import Any, TypeVar

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from linkding_mcp_server.config import Settings
from linkding_mcp_server.models import Bookmark, BookmarkCheck, BookmarkCreate, BookmarkList, BookmarkUpdate, TagList
from linkding_mcp_server.telemetry import (
    MetricsSink,
    NoOpMetricsSink,
    StructuredLogMetricsSink,
    normalize_endpoint,
)

# Configure structured logging for application use
logger = structlog.get_logger()

# Standard library logger used for SSL status and tenacity compatibility
_module_logger = logging.getLogger(__name__)

ResultT = TypeVar("ResultT")


class LinkDingError(Exception):
    """Base exception for LinkDing API errors"""

    pass


class RateLimitError(LinkDingError):
    """Raised when LinkDing or the local limiter rejects a request."""

    pass


def _resolve_ssl_verify(settings: Settings) -> bool | str:
    """Determine the httpx verify value from settings.

    Precedence: disabled > custom CA path > default (True).

    Args:
        settings: Application settings.

    Returns:
        False to skip verification, a CA bundle path string, or True for default.
    """
    if not settings.verify_ssl:
        return False
    if settings.ssl_cert_path:
        return settings.ssl_cert_path
    return True


def _log_ssl_status(settings: Settings) -> None:
    """Emit a log message describing the SSL verification configuration.

    Args:
        settings: Application settings.
    """
    if not settings.verify_ssl:
        _module_logger.warning(
            "SSL verification is DISABLED. Traffic is not protected against MITM attacks. "
            "Only use this for trusted local or self-signed setups."
        )
    elif settings.ssl_cert_path:
        _module_logger.info("SSL verification enabled with custom CA bundle: %s", settings.ssl_cert_path)
    else:
        _module_logger.info("SSL verification enabled (default system CA bundle).")


class LinkDingClient:
    """HTTP client for LinkDing API with retry and connection pooling"""

    def __init__(
        self,
        settings: Settings,
        metrics: MetricsSink | None = None,
    ):
        self.settings = settings
        self.client: httpx.AsyncClient | None = None
        self.metrics = metrics or (
            StructuredLogMetricsSink()
            if settings.observability_enabled
            else NoOpMetricsSink()
        )
        self.rate_limiter = RateLimiter(
            calls=settings.rate_limit_calls,
            period=settings.rate_limit_period,
            metrics=self.metrics,
        )
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._cache_timestamps: dict[str, float] = {}
        _log_ssl_status(settings)

    async def __aenter__(self):
        """Enter async context"""
        verify = _resolve_ssl_verify(self.settings)

        self.client = httpx.AsyncClient(
            base_url=f"{str(self.settings.linkding_url).rstrip('/')}/api",
            headers={"Authorization": f"Token {self.settings.linkding_api_token}"},
            timeout=httpx.Timeout(self.settings.request_timeout),
            limits=httpx.Limits(
                max_connections=self.settings.max_connections,
                max_keepalive_connections=self.settings.max_keepalive_connections,
                keepalive_expiry=self.settings.keepalive_expiry,
            ),
            verify=verify,
        )
        logger.info(
            "client_initialized",
            base_url=str(self.settings.linkding_url),
            masked_token=self.settings.get_masked_token(),
            timeout=self.settings.request_timeout,
            ssl_verify=self.settings.verify_ssl,
            ssl_cert=self.settings.ssl_cert_path or "default",
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if self.client:
            await self.client.aclose()
            logger.info("client_closed")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _request_with_retry(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make one retry-managed HTTP request."""
        if not self.client:
            raise LinkDingError("Client not initialized. Use async context manager.")

        # Apply rate limiting
        await self.rate_limiter.check()

        log = logger.bind(method=method, endpoint=endpoint)
        log.debug("making_request")
        started_at = time.perf_counter()
        metric_attributes = {
            "method": method.upper(),
            "endpoint": normalize_endpoint(endpoint),
        }

        try:
            response = await self.client.request(method, endpoint, **kwargs)
            log.debug("request_completed", status_code=response.status_code)
            duration_ms = (time.perf_counter() - started_at) * 1000

            # Check for rate limiting response
            if response.status_code == 429:
                self.metrics.record(
                    "linkding.http.request",
                    **metric_attributes,
                    status_code=429,
                    outcome="rate_limited",
                    duration_ms=duration_ms,
                )
                raise RateLimitError("Rate limit exceeded")

            self.metrics.record(
                "linkding.http.request",
                **metric_attributes,
                status_code=response.status_code,
                outcome="success" if response.status_code < 400 else "error",
                duration_ms=duration_ms,
            )
            return response

        except httpx.NetworkError as e:
            log.error("network_error", error=str(e))
            self.metrics.record(
                "linkding.http.request",
                **metric_attributes,
                outcome="error",
                error_type=type(e).__name__,
                duration_ms=(time.perf_counter() - started_at) * 1000,
            )
            raise
        except httpx.TimeoutException as e:
            log.error("timeout_error", error=str(e))
            self.metrics.record(
                "linkding.http.request",
                **metric_attributes,
                outcome="error",
                error_type=type(e).__name__,
                duration_ms=(time.perf_counter() - started_at) * 1000,
            )
            raise

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make an HTTP request and expose expected failures as domain errors."""
        try:
            return await self._request_with_retry(method, endpoint, **kwargs)
        except LinkDingError:
            raise
        except (httpx.NetworkError, httpx.TimeoutException) as error:
            raise LinkDingError(f"LinkDing request failed: {error}") from error

    async def handle_api_error(self, response: httpx.Response) -> str:
        """Extract meaningful error message from API response"""
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                if "detail" in error_data:
                    return f"API Error: {error_data['detail']}"
                elif "error" in error_data:
                    return f"API Error: {error_data['error']}"
                else:
                    # Try to extract any error messages from nested structures
                    for key in ["message", "msg", "reason"]:
                        if key in error_data:
                            return f"API Error: {error_data[key]}"
                    return f"API Error: {error_data}"
            else:
                return f"API Error: {error_data}"
        except Exception:
            return f"HTTP {response.status_code}: {response.text[:200]}"

    async def get_bookmarks(self, archived: bool = False, **params) -> BookmarkList:
        """Get bookmarks from API"""
        endpoint = "/bookmarks/archived/" if archived else "/bookmarks/"
        response = await self._make_request("GET", endpoint, params=params)

        if response.status_code != 200:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        data = response.json()
        return BookmarkList(**data)

    async def create_bookmark(self, bookmark: BookmarkCreate) -> Bookmark:
        """Create a new bookmark"""
        payload = {
            "url": str(bookmark.url),
            "is_archived": bookmark.is_archived,
            "unread": bookmark.unread,
            "shared": bookmark.shared,
        }

        if bookmark.title:
            payload["title"] = bookmark.title
        if bookmark.description:
            payload["description"] = bookmark.description
        if bookmark.notes:
            payload["notes"] = bookmark.notes
        if bookmark.tags:
            payload["tag_names"] = bookmark.tags

        response = await self._make_request("POST", "/bookmarks/", json=payload)

        if response.status_code not in [200, 201]:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        data = response.json()
        return Bookmark(**data)

    async def get_bookmark(self, bookmark_id: int) -> Bookmark:
        """Get a specific bookmark by ID"""
        response = await self._make_request("GET", f"/bookmarks/{bookmark_id}/")

        if response.status_code == 404:
            raise LinkDingError(f"Bookmark with ID {bookmark_id} not found")
        elif response.status_code != 200:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        data = response.json()
        return Bookmark(**data)

    def _build_update_payload(self, update: BookmarkUpdate) -> dict[str, Any]:
        """Build API payload from update model, including only non-None fields."""
        field_mapping = {
            "url": ("url", lambda v: str(v)),
            "title": ("title", None),
            "description": ("description", None),
            "notes": ("notes", None),
            "tags": ("tag_names", None),
            "is_archived": ("is_archived", None),
            "unread": ("unread", None),
            "shared": ("shared", None),
        }
        payload = {}
        for attr, (api_key, transform) in field_mapping.items():
            value = getattr(update, attr)
            if value is not None:
                payload[api_key] = transform(value) if transform else value
        return payload

    async def update_bookmark(self, bookmark_id: int, update: BookmarkUpdate) -> Bookmark:
        """Update an existing bookmark"""
        payload = self._build_update_payload(update)

        if not payload:
            raise ValueError("No fields provided to update")

        response = await self._make_request("PATCH", f"/bookmarks/{bookmark_id}/", json=payload)

        if response.status_code == 404:
            raise LinkDingError(f"Bookmark with ID {bookmark_id} not found")
        elif response.status_code != 200:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        data = response.json()
        return Bookmark(**data)

    async def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark"""
        response = await self._make_request("DELETE", f"/bookmarks/{bookmark_id}/")

        if response.status_code == 404:
            raise LinkDingError(f"Bookmark with ID {bookmark_id} not found")
        elif response.status_code != 204:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        return True

    async def archive_bookmark(self, bookmark_id: int) -> bool:
        """Archive a bookmark"""
        response = await self._make_request("POST", f"/bookmarks/{bookmark_id}/archive/")

        if response.status_code == 404:
            raise LinkDingError(f"Bookmark with ID {bookmark_id} not found")
        elif response.status_code != 204:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        return True

    async def unarchive_bookmark(self, bookmark_id: int) -> bool:
        """Unarchive a bookmark"""
        response = await self._make_request("POST", f"/bookmarks/{bookmark_id}/unarchive/")

        if response.status_code == 404:
            raise LinkDingError(f"Bookmark with ID {bookmark_id} not found")
        elif response.status_code != 204:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        return True

    async def check_url(self, url: str) -> BookmarkCheck:
        """Check if a URL is already bookmarked"""
        response = await self._make_request("GET", "/bookmarks/check/", params={"url": url})

        if response.status_code != 200:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        data = response.json()
        return BookmarkCheck(**data)

    async def get_tags(self, limit: int = 100, offset: int = 0) -> TagList:
        """Get list of tags"""
        # Check cache if enabled
        cache_key = f"tags_{limit}_{offset}"
        if self.settings.cache_ttl > 0:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        response = await self._make_request("GET", "/tags/", params={"limit": limit, "offset": offset})

        if response.status_code != 200:
            error = await self.handle_api_error(response)
            raise LinkDingError(error)

        data = response.json()
        result = TagList(**data)

        # Cache result if enabled
        if self.settings.cache_ttl > 0:
            self._add_to_cache(cache_key, result)

        return result

    async def paginate_results(
        self,
        endpoint: str,
        model_class: Callable[..., ResultT],
        params: dict[str, Any],
        max_results: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[ResultT]:
        """Stream model instances from a paginated API endpoint.

        Results are yielded one at a time so callers do not need to retain the
        complete result set in memory. ``max_results`` remains available for
        callers that limit by item count, while ``max_pages`` bounds the number
        of API pages fetched.
        """
        next_url = endpoint
        yielded_results = 0
        fetched_pages = 0

        while next_url:
            if max_results and yielded_results >= max_results:
                return
            if max_pages and fetched_pages >= max_pages:
                return

            if next_url == endpoint:
                # First request with params
                response = await self._make_request("GET", next_url, params=params)
            else:
                # Follow pagination URL
                response = await self._make_request("GET", next_url)

            if response.status_code != 200:
                error = await self.handle_api_error(response)
                raise LinkDingError(error)

            data = response.json()
            fetched_pages += 1

            for item in data.get("results", []):
                if max_results and yielded_results >= max_results:
                    return
                yield model_class(**item)
                yielded_results += 1

            # Get next page URL
            next_url = data.get("next")
            if next_url:
                # Extract path from full URL
                next_url = next_url.replace(str(self.settings.linkding_url), "")

    def _get_from_cache(self, key: str) -> Any | None:
        """Get item from cache if not expired.

        Moves the accessed key to the end of the OrderedDict to mark it as
        most recently used. Expired entries are removed on access.

        Args:
            key: Cache key to look up.

        Returns:
            The cached value, or None if missing or expired.
        """
        if key in self._cache:
            timestamp = self._cache_timestamps.get(key, 0)
            if time.time() - timestamp < self.settings.cache_ttl:
                self._cache.move_to_end(key)
                logger.debug("cache_hit", key=key)
                self.metrics.record("linkding.cache.access", outcome="hit")
                return self._cache[key]
            else:
                del self._cache[key]
                self._cache_timestamps.pop(key, None)
                self.metrics.record("linkding.cache.access", outcome="expired")
                return None
        self.metrics.record("linkding.cache.access", outcome="miss")
        return None

    def _add_to_cache(self, key: str, value: Any):
        """Add item to cache with LRU eviction.

        When the cache is at capacity, the least recently used entry is evicted
        before inserting the new value.

        Args:
            key: Cache key.
            value: Value to store.
        """
        if key in self._cache:
            self._cache.move_to_end(key)
        elif len(self._cache) >= self.settings.cache_max_size:
            evicted_key, _ = self._cache.popitem(last=False)
            self._cache_timestamps.pop(evicted_key, None)
            logger.debug("cache_evicted", key=evicted_key)
            self.metrics.record("linkding.cache.eviction", reason="capacity")
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()
        self.metrics.record("linkding.cache.size", entries=len(self._cache))
        logger.debug("cache_set", key=key)


class RateLimiter:
    """Simple rate limiter for API requests"""

    def __init__(
        self,
        calls: int,
        period: int,
        metrics: MetricsSink | None = None,
    ):
        self.calls = calls
        self.period = period
        self.timestamps: list[float] = []
        self.metrics = metrics or NoOpMetricsSink()

    async def check(self):
        """Check if request is allowed under rate limit"""
        now = time.time()

        # Remove old timestamps
        self.timestamps = [ts for ts in self.timestamps if now - ts < self.period]
        self.metrics.record(
            "linkding.rate_limit.usage",
            used=len(self.timestamps),
            limit=self.calls,
            utilization=len(self.timestamps) / self.calls,
        )

        if len(self.timestamps) >= self.calls:
            # Calculate wait time
            oldest = min(self.timestamps)
            wait_time = self.period - (now - oldest) + 0.1
            if wait_time > 0:
                logger.warning("rate_limit_wait", wait_seconds=wait_time)
                self.metrics.record(
                    "linkding.rate_limit.wait",
                    duration_ms=wait_time * 1000,
                )
                await asyncio.sleep(wait_time)

        self.timestamps.append(now)
