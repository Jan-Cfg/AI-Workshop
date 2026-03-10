# System Architecture – MCP GitHub Integration

This project demonstrates how an AI assistant can interact with external systems using the Model Context Protocol (MCP).

The system integrates Claude Desktop with the GitHub MCP server to retrieve repository data.

---

# High Level Architecture

```
User Prompt
     │
     ▼
Claude Desktop (LLM)
     │
     ▼
Tool Selection via MCP
     │
     ▼
GitHub MCP Server
     │
     ▼
GitHub API
     │
     ▼
Response returned to Claude
```

---

# Component Overview

## 1. User Prompt

The user provides a natural language instruction such as:

```
Show the latest commits from my GitHub repository TestApp
```

This prompt is processed by Claude.

---

## 2. Claude Desktop

Claude acts as the intelligent agent.

Responsibilities:

* Understand natural language
* Identify the required action
* Select the correct MCP tool
* Send structured tool input

Example tool call:

```
Tool: list_commits
Repository: TestApp
Owner: vsingh-107885
```

---

## 3. MCP (Model Context Protocol)

MCP is a standard that allows AI systems to connect with external tools.

Key capabilities:

* Tool discovery
* Tool invocation
* Standardized communication between AI and tools

Claude uses MCP to discover and call GitHub tools.

---

## 4. GitHub MCP Server

The GitHub MCP server acts as a bridge between Claude and GitHub APIs.

Responsibilities:

* Expose GitHub operations as tools
* Authenticate using GitHub Personal Access Token
* Send API requests to GitHub
* Return structured responses

Example tools:

* list_commits
* create_issue
* create_pull_request
* list_repositories

---

## 5. GitHub API

The GitHub API is used to fetch repository data.

Example endpoint:

```
GET /repos/{owner}/{repo}/commits
```

The MCP server uses the API to retrieve commit information.

---

# Example Execution Flow

Step 1: User enters prompt

```
Show the latest commits from my repository AI-Workshop-vs
```

Step 2: Claude understands the request

Step 3: Claude selects GitHub MCP tool `list_commits`

Step 4: MCP server receives tool request

Step 5: MCP server calls GitHub API

Step 6: GitHub returns commit data

Step 7: MCP server returns response to Claude

Step 8: Claude displays commit information to the user

---

# Architecture Diagram

```
+-------------+
|   User      |
+-------------+
       │
       ▼
+-------------+
| Claude LLM  |
+-------------+
       │
       ▼
+-------------+
| MCP Protocol|
+-------------+
       │
       ▼
+--------------------+
| GitHub MCP Server  |
+--------------------+
       │
       ▼
+--------------------+
|   GitHub API       |
+--------------------+
```

---

# Benefits of MCP

Using MCP provides several advantages:

* Standardized tool integration
* Secure API access
* Easy extension with new tools
* Enables agent-based workflows

---

# Conclusion

This project demonstrates how AI systems can interact with external services through MCP servers.
By connecting Claude Desktop to the GitHub MCP server, we enable AI-assisted access to repository data such as commits and issues.
