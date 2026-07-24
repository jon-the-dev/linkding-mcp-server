# TODO — linkding-mcp-server

## Current Sprint (2026-03-09)

- [x] #6 — Use getpass for token input in setup (P1: security bug)
- [x] #3 — Add SSL/TLS verification configuration (P1: security enhancement)
- [x] #9 — Reduce update_bookmark() cyclomatic complexity (P3: refactoring)
- [x] #10 — Move time imports to module level (P4: refactoring)
- [x] #4 — Implement cache size limits (P3: performance)
- [x] #11 — Fix hardcoded version string in server.py (P4: maintenance)

## Next Up

- [ ] #1 — Prepare this for deployment on PyPI (P2: high enhancement)

## Backlog — Medium

- [ ] #2 — Refactor create_mcp_server() to reduce cyclomatic complexity
- [ ] #5 — Replace settings singleton with dependency injection
- [ ] #8 — Optimize pagination for large datasets
- [ ] #18 — Improve test coverage and add integration tests

## Backlog — Low

- [ ] #15 — Add Python 3.12 version check fix
- [ ] #7 — Update ruff config to lint section
- [ ] #12 — Standardize error handling patterns
- [ ] #13 — Extract logging configuration to separate module
- [ ] #14 — Document rate limiting limitations for multi-instance deployments
- [ ] #16 — Add interface/protocol definitions for LinkDingClient
- [ ] #17 — Add monitoring and metrics
