# Prompt: Fetch Repository Commits

## Objective
Use GitHub MCP server to retrieve commits from a repository.

## User Prompt
Show all commits from my repository <repo-name>.

## AI Tool Selected
GitHub MCP Tool:
list_commits

## Tool Input
{
  "owner": "<username>",
  "repo": "<repo-name>"
}

## Output
List of commits including:
- Commit SHA
- Message
- Author
- Date
