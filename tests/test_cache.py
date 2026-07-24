"""Tests for LRU cache functionality in LinkDingClient"""

import time
from unittest.mock import MagicMock

import pytest

from linkding_mcp_server.client import LinkDingClient


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.cache_ttl = 300
    settings.cache_max_size = 3
    settings.rate_limit_calls = 100
    settings.rate_limit_period = 60
    return settings


class TestLRUCache:
    def test_cache_hit(self, mock_settings):
        client = LinkDingClient(mock_settings)
        client._add_to_cache("key1", "value1")
        assert client._get_from_cache("key1") == "value1"

    def test_cache_miss(self, mock_settings):
        client = LinkDingClient(mock_settings)
        assert client._get_from_cache("missing") is None

    def test_cache_eviction(self, mock_settings):
        client = LinkDingClient(mock_settings)
        client._add_to_cache("key1", "value1")
        client._add_to_cache("key2", "value2")
        client._add_to_cache("key3", "value3")
        client._add_to_cache("key4", "value4")
        assert client._get_from_cache("key1") is None
        assert client._get_from_cache("key4") == "value4"

    def test_cache_storage_remains_bounded_under_load(self, mock_settings):
        client = LinkDingClient(mock_settings)

        for index in range(10_000):
            client._add_to_cache(f"key{index}", f"value{index}")

        assert len(client._cache) == mock_settings.cache_max_size
        assert len(client._cache_timestamps) == mock_settings.cache_max_size
        assert client._cache.keys() == client._cache_timestamps.keys()

    def test_cache_lru_order(self, mock_settings):
        client = LinkDingClient(mock_settings)
        client._add_to_cache("key1", "value1")
        client._add_to_cache("key2", "value2")
        client._add_to_cache("key3", "value3")
        client._get_from_cache("key1")  # access key1, making key2 LRU
        client._add_to_cache("key4", "value4")
        assert client._get_from_cache("key2") is None
        assert client._get_from_cache("key1") == "value1"

    def test_cache_expiry(self, mock_settings):
        mock_settings.cache_ttl = 1
        client = LinkDingClient(mock_settings)
        client._add_to_cache("key1", "value1")
        time.sleep(1.1)
        assert client._get_from_cache("key1") is None
