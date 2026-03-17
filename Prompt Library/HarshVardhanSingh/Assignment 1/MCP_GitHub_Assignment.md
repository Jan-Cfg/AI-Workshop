
# MCP Example: GitHub MCP Server with create_issue Tool

## Selected MCP Server and Tool

### MCP Server
**GitHub MCP Server** – provides GitHub integration (repositories, issues, PRs, files).

### Tool Used
**create_issue** – creates a GitHub issue programmatically.

---

## Architecture Overview

Client (AI agent / script)
↓ MCP (JSON-RPC over stdio)
GitHub MCP Server
↓ GitHub REST API
GitHub Repository

---

## Step 1: Run GitHub MCP Server

```bash
export GITHUB_TOKEN=ghp_your_personal_access_token
npx @modelcontextprotocol/server-github
```

---

## Step 2: Tool Schema (Conceptual)

```json
{
  "name": "create_issue",
  "description": "Create a GitHub issue in a repository",
  "inputSchema": {
    "type": "object",
    "properties": {
      "owner": { "type": "string" },
      "repo": { "type": "string" },
      "title": { "type": "string" },
      "body": { "type": "string" }
    },
    "required": ["owner", "repo", "title"]
  }
}
```

---

## Step 3: Sample MCP Client (Node.js)

```javascript
import { spawn } from "child_process";
import readline from "readline";

const server = spawn("npx", ["@modelcontextprotocol/server-github"], {
  stdio: ["pipe", "pipe", "inherit"],
  env: { ...process.env, GITHUB_TOKEN: process.env.GITHUB_TOKEN }
});

const rl = readline.createInterface({ input: server.stdout });
rl.on("line", line => console.log("MCP RESPONSE:", line));

const request = {
  jsonrpc: "2.0",
  id: 1,
  method: "tools/call",
  params: {
    name: "create_issue",
    arguments: {
      owner: "your-github-username",
      repo: "demo-repo",
      title: "Bug: Login not working",
      body: "Steps to reproduce..."
    }
  }
};

server.stdin.write(JSON.stringify(request) + "
");
```

---

## Alternative CLI-style Invocation

```bash
echo '{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "create_issue",
    "arguments": {
      "owner": "your-github-username",
      "repo": "demo-repo",
      "title": "Docs missing",
      "body": "README needs setup instructions"
    }
  }
}' | npx @modelcontextprotocol/server-github
```

---

## Use Cases

- AI DevOps bots
- Automated bug reporting
- Code review automation
- Documentation assistants
