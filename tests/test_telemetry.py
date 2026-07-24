"""Offline tests for dependency-free observability."""

from unittest.mock import AsyncMock

import httpx
import pytest

from linkding_mcp_server.client import LinkDingClient, RateLimiter
from linkding_mcp_server.config import Settings
from linkding_mcp_server.telemetry import (
    NoOpMetricsSink,
    StructuredLogMetricsSink,
    normalize_endpoint,
)


class RecordingSink:
    def __init__(self):
        self.events = []

    def record(self, event, **attributes):
        self.events.append((event, attributes))

    def matching(self, event):
        return [attributes for name, attributes in self.events if name == event]


@pytest.fixture
def settings():
    return Settings(
        linkding_url="https://linkding.example.com",
        linkding_api_token="token",
        cache_ttl=300,
        cache_max_size=2,
    )


def test_endpoint_normalization_redacts_ids_and_queries():
    assert (
        normalize_endpoint(
            "https://linkding.example.com/api/bookmarks/123/?token=secret"
        )
        == "/api/bookmarks/{id}/"
    )


def test_observability_is_opt_in(settings):
    assert isinstance(LinkDingClient(settings).metrics, NoOpMetricsSink)

    enabled = settings.model_copy(update={"observability_enabled": True})
    assert isinstance(LinkDingClient(enabled).metrics, StructuredLogMetricsSink)


@pytest.mark.asyncio
async def test_request_metrics_capture_status_latency_and_redacted_route(settings):
    metrics = RecordingSink()
    client = LinkDingClient(settings, metrics=metrics)

    async with client:
        client.client.request = AsyncMock(
            return_value=httpx.Response(
                200,
                json={"results": []},
                request=httpx.Request("GET", "https://linkding.example.com"),
            )
        )
        await client._make_request(
            "GET",
            "/bookmarks/123/?api_token=must-not-appear",
        )

    request_event = metrics.matching("linkding.http.request")[-1]
    assert request_event["method"] == "GET"
    assert request_event["endpoint"] == "/bookmarks/{id}/"
    assert request_event["status_code"] == 200
    assert request_event["outcome"] == "success"
    assert request_event["duration_ms"] >= 0
    assert "must-not-appear" not in str(request_event)


@pytest.mark.asyncio
async def test_request_metrics_classify_rate_limits(settings):
    metrics = RecordingSink()
    client = LinkDingClient(settings, metrics=metrics)

    async with client:
        client.client.request = AsyncMock(
            return_value=httpx.Response(
                429,
                request=httpx.Request("GET", "https://linkding.example.com"),
            )
        )
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await client._make_request("GET", "/bookmarks/")

    assert metrics.matching("linkding.http.request")[-1]["outcome"] == "rate_limited"


def test_cache_metrics_cover_miss_hit_expiry_and_eviction(settings, monkeypatch):
    metrics = RecordingSink()
    client = LinkDingClient(settings, metrics=metrics)
    clock = iter([10.0, 10.0, 10.0, 10.0, 400.0])
    monkeypatch.setattr("linkding_mcp_server.client.time.time", lambda: next(clock))

    assert client._get_from_cache("missing") is None
    client._add_to_cache("one", 1)
    assert client._get_from_cache("one") == 1
    client._add_to_cache("two", 2)
    client._add_to_cache("three", 3)
    assert client._get_from_cache("two") is None

    outcomes = [
        event["outcome"] for event in metrics.matching("linkding.cache.access")
    ]
    assert outcomes == ["miss", "hit", "expired"]
    assert metrics.matching("linkding.cache.eviction") == [{"reason": "capacity"}]
    assert metrics.matching("linkding.cache.size")[-1]["entries"] == 2


@pytest.mark.asyncio
async def test_rate_limiter_metrics_report_usage_and_wait(monkeypatch):
    metrics = RecordingSink()
    limiter = RateLimiter(calls=1, period=10, metrics=metrics)
    limiter.timestamps = [100.0]
    sleep = AsyncMock()
    monkeypatch.setattr("linkding_mcp_server.client.time.time", lambda: 100.0)
    monkeypatch.setattr("linkding_mcp_server.client.asyncio.sleep", sleep)

    await limiter.check()

    assert metrics.matching("linkding.rate_limit.usage") == [
        {"used": 1, "limit": 1, "utilization": 1.0}
    ]
    assert metrics.matching("linkding.rate_limit.wait")[0]["duration_ms"] == pytest.approx(10100.0)
    sleep.assert_awaited_once_with(10.1)
