# Setup Guide – GitHub MCP Server with Claude Desktop

This guide explains how to run the GitHub MCP server using Docker and interact with it using Claude Desktop.

---

# Prerequisites

Before starting, install the following software:

* Docker Desktop
* Python 3.10+ (Optional here but often required as Many Model Context Protocol (MCP) servers and tools are built using the Python MCP SDK, which requires Python 3.10+ to run)
* Claude Desktop
* Git

Tools used in this project:

* GitHub MCP Server
* Claude Desktop
* Docker
* GitHub Personal Access Token

---

# Step 1: Create a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **Generate new token**
3. Select the following permissions:

* repo
* read:org
* workflow

4. Copy and save the token securely.

Example:

```
ghp_xxxxxxxxxxxxxxxxxxxxx
```

---

# Step 2: Set GitHub Token as Environment Variable

Open terminal and run:

Windows (PowerShell):

```
setx GITHUB_PERSONAL_ACCESS_TOKEN "your_token_here"
```

Restart the terminal after setting the variable.

Verify it:

```
echo %GITHUB_PERSONAL_ACCESS_TOKEN%
```

---

# Step 3: Pull GitHub MCP Docker Image

Run the following command:

```
docker pull ghcr.io/modelcontextprotocol/servers/github:latest
```

---

# Step 4: Run GitHub MCP Server

Start the container:

```
docker run -e GITHUB_PERSONAL_ACCESS_TOKEN=%GITHUB_PERSONAL_ACCESS_TOKEN% ghcr.io/modelcontextprotocol/servers/github
```

If configured correctly, the server will start and display:

```
GitHub MCP Server running on stdio
```

---

# Step 5: Configure Claude Desktop

Open Claude Desktop configuration file.

Location:

```
C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json
```

Add the MCP server configuration:

```
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/modelcontextprotocol/servers/github"
      ]
    }
  }
}
```

Restart Claude Desktop after saving the configuration.

---

# Step 6: Test the MCP Tool

Open Claude Desktop and use the following prompt:

```
Show the latest commits from my GitHub repository TestApp
```

Claude will:

1. Understand the request
2. Select the GitHub MCP tool
3. Call the `list_commits` tool
4. Fetch commits from GitHub

---

# Expected Output

Claude will return commit details such as:

* Commit message
* Author
* Commit date
* Commit SHA

Example:

```
Commit: Fix README documentation
Author: Vishal Singh
Date: 2026-03-07
```

---

# Troubleshooting

## MCP container stops immediately

Check that the GitHub token is set correctly:

```
echo %GITHUB_PERSONAL_ACCESS_TOKEN%
```

## Docker container exits

Ensure the token has the **repo permission** enabled.

## Claude not detecting MCP tools

Restart Claude Desktop after editing the configuration file.

---

# Summary

This setup demonstrates how Claude Desktop can interact with external tools through MCP servers.
In this project, the GitHub MCP server enables Claude to access repository information such as commits.
