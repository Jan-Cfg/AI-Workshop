import os
import json
import httpx
from mcp.types import CallToolResult, TextContent, Tool

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

async def list_repositories(owner: str) -> str:
    url = f"https://api.github.com/users/{owner}/repos"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code == 200:
            repos = response.json()
            return json.dumps([
                {"name": repo["name"], "url": repo["html_url"], "stars": repo["stargazers_count"]}
                for repo in repos[:10]
            ])
        return json.dumps({"error": response.text, "status": response.status_code})

async def get_repository(owner: str, repo: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return json.dumps({
                "name": data["name"],
                "description": data.get("description"),
                "url": data["html_url"],
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "language": data.get("language"),
                "open_issues": data["open_issues_count"]
            })
        return json.dumps({"error": response.text, "status": response.status_code})

async def get_user_profile(username: str) -> str:
    url = f"https://api.github.com/users/{username}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return json.dumps({
                "name": data.get("name"),
                "bio": data.get("bio"),
                "company": data.get("company"),
                "location": data.get("location"),
                "public_repos": data["public_repos"],
                "followers": data["followers"],
                "following": data["following"]
            })
        return json.dumps({"error": response.text, "status": response.status_code})

async def create_issue(owner: str, repo: str, title: str, body: str) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    payload = {"title": title, "body": body}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=HEADERS, json=payload)
        if response.status_code == 201:
            issue = response.json()
            return json.dumps({
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"]
            })
        return json.dumps({"error": response.text, "status": response.status_code})

TOOLS = [
    Tool(
        name="list_repositories",
        description="List repositories for a GitHub user or organization",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "GitHub username or organization"}
            },
            "required": ["owner"]
        }
    ),
    Tool(
        name="get_repository",
        description="Get detailed information about a specific repository",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"}
            },
            "required": ["owner", "repo"]
        }
    ),
    Tool(
        name="get_user_profile",
        description="Get GitHub user profile and statistics",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "GitHub username"}
            },
            "required": ["username"]
        }
    ),
    Tool(
        name="create_issue",
        description="Create a new issue in a repository",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue description"}
            },
            "required": ["owner", "repo", "title", "body"]
        }
    )
]


def list_tools() -> list[Tool]:
    return TOOLS

async def call_tool(name: str, arguments: dict) -> CallToolResult:
    if name == "list_repositories":
        payload = await list_repositories(**arguments)
    elif name == "get_repository":
        payload = await get_repository(**arguments)
    elif name == "get_user_profile":
        payload = await get_user_profile(**arguments)
    elif name == "create_issue":
        payload = await create_issue(**arguments)
    else:
        payload = json.dumps({"error": f"Unknown tool: {name}"})

    return CallToolResult(content=[TextContent(type="text", text=payload)])

if __name__ == "__main__":
    print("GitHub MCP Server minimal module")
    print("Available tools:", ", ".join(tool.name for tool in TOOLS))
