# Assignment‑2 — MCP Server Usage

## MCP Server Selected
**Azure DevOps MCP Server**

This MCP server exposes Azure DevOps capabilities such as Boards (work items),
Repositories, Pipelines, and Test Plans as callable tools for AI clients.

---

## Tool Selected
**repo_list_repos_by_project**

This tool retrieves the list of Git repositories available under a given
Azure DevOps project. It is a read‑only operation and safe to use.

---

## Sample Usage (Client Write‑up)

An AI client can invoke the `repo_list_repos_by_project` tool with the
following input parameters:

```json
{
  "org": "sample-organization",
  "project": "sample-project",
  "page": 1,
  "pageSize": 10
}
