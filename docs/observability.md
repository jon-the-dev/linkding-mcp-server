# Observability

LinkDing MCP Server can emit dependency-free structured metric events through
its existing logging pipeline. Metrics are disabled by default.

```env
LINKDING_OBSERVABILITY_ENABLED=true
```

No collector or active LinkDing server is required. JSON log processors,
StatsD bridges, Prometheus log collectors, and OpenTelemetry log pipelines can
map the stable event schema to their preferred backend.

## Event Schema

| Event | Attributes | Meaning |
|-------|------------|---------|
| `linkding.http.request` | `method`, `endpoint`, `status_code`, `outcome`, `error_type`, `duration_ms` | One event per HTTP attempt |
| `linkding.cache.access` | `outcome` | Cache hit, miss, or expiry |
| `linkding.cache.eviction` | `reason` | Capacity eviction |
| `linkding.cache.size` | `entries` | Current bounded cache entry count |
| `linkding.rate_limit.usage` | `used`, `limit`, `utilization` | Local limiter usage before a request |
| `linkding.rate_limit.wait` | `duration_ms` | Local throttling delay |

`status_code` is absent for transport errors. `error_type` contains only the
exception class, never its message.

## Privacy and Cardinality

- URL queries are removed.
- Numeric resource IDs become `{id}`.
- API tokens, bookmark URLs, titles, tags, request bodies, and exception
  messages are never metric attributes.
- Endpoint, method, outcome, and error type are bounded dimensions suitable
  for aggregation.

The rate-limit events describe this process's local limiter. They do not claim
to represent LinkDing's server-side quota or usage by other processes.

## Backend Mapping

Collectors should derive counters and histograms from events:

- Count `linkding.http.request` by method, endpoint, status, and outcome.
- Build latency distributions from `duration_ms`.
- Count cache access outcomes to calculate hit rate.
- Track local saturation from `utilization` and wait events.

OpenTelemetry is an adapter boundary, not a required dependency. A deployment
may translate these events into OTEL metrics/logs without changing the server
contract. If no collector is configured, structured events remain ordinary
application logs.

## Offline Verification

The test suite injects a recording metrics sink and mocked HTTP responses:

```bash
uv run pytest tests/test_telemetry.py -v
```

This verifies classification, latency fields, redaction, cache events, and
rate-limiter events without network access or LinkDing credentials.
