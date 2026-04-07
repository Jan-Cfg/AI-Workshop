# Assignment 2 - MCP Server and Tool

## MCP Server Selected
GitHub MCP Server  
Reference: https://github.com/github/github-mcp-server

## Tool Selected
Issue listing tool from the `issues` toolset (tool name depends on server version).  
This sample client first lists available tools, then optionally calls one selected issue-related tool.

## What This Python Sample Demonstrates
- Starts GitHub MCP server through Docker in read-only mode
- Initializes an MCP session over stdio
- Lists available tools from the server
- Calls a selected tool using `tools/call`

## File
- `github_mcp_client.py`

## Prerequisites
1. Docker Desktop installed and running
2. Python 3.10+
3. GitHub Personal Access Token with minimum read permissions

## Usage (PowerShell)
1. Set token

   $env:GITHUB_PERSONAL_ACCESS_TOKEN="<your_token>"

2. List tools from issues toolset

   python github_mcp_client.py --toolsets issues

3. Call one issue-related tool (example)

   python github_mcp_client.py --toolsets issues --call-tool issue_read --tool-args "{\"owner\":\"octocat\",\"repo\":\"Hello-World\"}"

If `issue_read` is not present in your server version, use the exact tool name shown in step 2.

## Notes
- The assignment requirement asks for one MCP server, one tool, and usage sample. This submission uses GitHub MCP + issue listing flow.
- You can switch to PR use cases by running with `--toolsets pull_requests` and calling a PR-related tool shown in the tool list.
