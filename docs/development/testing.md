# Testing Guide

The test suite validates the MCP server without requiring a running LinkDing
instance, network access, Docker, or real credentials.

## Test Layers

| Layer | Files | Purpose |
|-------|-------|---------|
| Unit | `tests/test_*.py` | Models, configuration, client behavior, cache, telemetry, setup, and entry points |
| MCP integration | `tests/test_tools_integration.py` | FastMCP through every tool and the production HTTP client |
| Concurrency | `tests/test_tools_integration.py` | 50 concurrent operations with isolated request state |
| Performance | `tests/test_tools_integration.py` | Deterministic 100-call in-process baseline |

## Offline LinkDing Boundary

Integration tests use `httpx.MockTransport` as an in-process LinkDing API.
Requests still travel through:

```text
FastMCP Client
  -> registered MCP tool
  -> protocol-injected production LinkDingClient
  -> authentication and request serialization
  -> httpx.MockTransport
  -> response/status parsing and Pydantic models
  -> MCP response content
```

All ten registered tools have success and upstream-failure coverage. This is
the default integration strategy when no disposable LinkDing server exists.
A manual real-server smoke test can supplement it before a release, but is not
required by CI.

## Commands

Install the project and development extras:

```bash
uv sync --extra dev
```

Run the complete suite:

```bash
uv run pytest
```

Run only offline integration tests:

```bash
uv run pytest -m integration -v
```

Run everything except the performance baseline:

```bash
uv run pytest -m "not performance"
```

Run the deterministic load baseline:

```bash
uv run pytest -m performance -v --durations=10
```

Run lint:

```bash
uv run ruff check linkding_mcp_server tests
```

## Coverage Gate

CI enforces at least 90% whole-package statement coverage:

```bash
uv run pytest -m "not performance" \
  --cov=linkding_mcp_server \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-fail-under=90
```

Coverage includes package, CLI, server, setup, client, tools, protocols,
telemetry, and logging configuration. It is not limited to selected modules.

## Concurrency and Performance Interpretation

The concurrency test asserts that 50 simultaneous MCP calls retain independent
offsets/results and complete the exact expected request count.

The performance test runs 100 concurrent in-process MCP calls with a generous
10-second CI ceiling. It is a regression guardrail for the Python/MCP path,
not a production capacity claim. Network, LinkDing database, host, and storage
latency are intentionally excluded.

## Error and Security Testing

The suite covers:

- HTTP validation, authentication-style, not-found, rate-limit, and server
  failures;
- transport retries and exhausted network errors;
- stable client-domain to MCP error translation;
- destructive-action denial;
- token masking and telemetry endpoint redaction;
- cache bounds, expiry, and LRU eviction;
- SSL verification modes.

Test data must use obvious placeholders. Never put a real LinkDing URL, API
token, bookmark content, or credential in fixtures or captured output.

## Observability Testing

Observability tests inject an in-memory metrics sink and deterministic clocks:

```bash
uv run pytest tests/test_telemetry.py -v
```

They verify event classification, latency fields, endpoint redaction, cache
signals, and local rate-limiter signals without a collector.

## CI Behavior

GitHub Actions installs the locked development extra, runs scoped Ruff,
executes the 90% coverage gate, and runs the performance baseline. Mypy remains
explicitly advisory while the repository's existing annotation backlog is
addressed; its failures are visible and are not hidden behind shell fallbacks.
