# GitHub MCP Server

Minimal GitHub MCP example exposing GitHub operations through a local MCP server.

## Files
- `github_mcp_server.py` — minimal MCP server implementation
- `tests/test_github_mcp.py` — unit tests with mocked GitHub responses

## Run tests

```bash
pip install mcp httpx pytest pytest-asyncio
python -m pytest tests/
```

## Notes

This README has been stripped of implementation code and full documentation. The working code is now contained in `github_mcp_server.py` and verified through tests.
