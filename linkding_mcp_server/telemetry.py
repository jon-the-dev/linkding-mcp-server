"""Dependency-free observability contracts and structured metric events."""

import re
from typing import Any, Protocol
from urllib.parse import urlsplit

import structlog

_RESOURCE_ID = re.compile(r"(?<=/)\d+(?=/|$)")


class MetricsSink(Protocol):
    """Destination for low-cardinality metric events."""

    def record(self, event: str, **attributes: Any) -> None: ...


class NoOpMetricsSink:
    """Disabled metrics sink with near-zero overhead."""

    def record(self, event: str, **attributes: Any) -> None:
        """Discard a metric event."""


class StructuredLogMetricsSink:
    """Emit metric events through the existing structured logger."""

    def __init__(self) -> None:
        self._logger = structlog.get_logger("linkding_mcp_server.metrics")

    def record(self, event: str, **attributes: Any) -> None:
        """Write a metric event for collection by the runtime log pipeline."""
        self._logger.info("metric", metric=event, **attributes)


def normalize_endpoint(endpoint: str) -> str:
    """Remove query values and resource IDs from an HTTP endpoint."""
    path = urlsplit(endpoint).path or "/"
    return _RESOURCE_ID.sub("{id}", path)
