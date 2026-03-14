
import json
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from jira_client import JiraClient

# ── Load .env ──────────────────────────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

JIRA_URL = os.getenv("JIRA_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    print(
        "ERROR: Set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN in .env or as environment variables.",
        file=sys.stderr,
    )
    sys.exit(1)


# ── Shared Jira client (lifespan-managed) ──────────────────────────────────
_jira: JiraClient | None = None


@asynccontextmanager
async def lifespan(server):
    """Create and tear down the shared Jira client."""
    global _jira
    _jira = JiraClient(JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN)
    try:
        yield
    finally:
        await _jira.close()


def jira() -> JiraClient:
    assert _jira is not None, "Jira client not initialised (lifespan not started)"
    return _jira


# ── MCP Server ─────────────────────────────────────────────────────────────
mcp = FastMCP(
    "Jira MCP Server",
    description="Pull and update Jira issues, comments, sprints, and more.",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER: format issue data into a clean readable string
# ═══════════════════════════════════════════════════════════════════════════

def _fmt_issue(issue: dict) -> str:
    """Return a concise, human-readable summary of an issue dict."""
    fields = issue.get("fields", {})
    key = issue.get("key", "?")
    summary = fields.get("summary", "—")
    status = (fields.get("status") or {}).get("name", "—")
    assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
    priority = (fields.get("priority") or {}).get("name", "—")
    issue_type = (fields.get("issuetype") or {}).get("name", "—")
    created = fields.get("created", "—")
    updated = fields.get("updated", "—")
    description = fields.get("description", "") or ""
    labels = ", ".join(fields.get("labels", [])) or "—"

    lines = [
        f"## {key}: {summary}",
        f"",
        f"| Field       | Value              |",
        f"|-------------|--------------------|",
        f"| **Type**    | {issue_type}       |",
        f"| **Status**  | {status}           |",
        f"| **Priority**| {priority}         |",
        f"| **Assignee**| {assignee}         |",
        f"| **Labels**  | {labels}           |",
        f"| **Created** | {created}          |",
        f"| **Updated** | {updated}          |",
    ]
    if description:
        # Truncate very long descriptions
        desc_preview = description[:1000] + ("…" if len(description) > 1000 else "")
        lines += ["", "### Description", desc_preview]
    return "\n".join(lines)


def _fmt_issue_row(issue: dict) -> str:
    """Single-line summary for search results."""
    f = issue.get("fields", {})
    key = issue.get("key", "?")
    summary = f.get("summary", "—")[:80]
    status = (f.get("status") or {}).get("name", "—")
    assignee = (f.get("assignee") or {}).get("displayName", "Unassigned")
    priority = (f.get("priority") or {}).get("name", "—")
    return f"| {key} | {summary} | {status} | {priority} | {assignee} |"


# ═══════════════════════════════════════════════════════════════════════════
#  TOOLS
# ═══════════════════════════════════════════════════════════════════════════

# ── Get Issue ───────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_get_issue(issue_key: str) -> str:
    """
    Fetch a Jira issue by its key (e.g. PROJ-123).
    Returns detailed information including summary, status, assignee, priority,
    labels, description, created and updated dates.
    """
    issue = await jira().get_issue(issue_key)
    return _fmt_issue(issue)


# ── Search Issues ───────────────────────────────────────────────────────────

@mcp.tool()
async def jira_search_issues(
    jql: str,
    max_results: int = 20,
) -> str:
    """
    Search for Jira issues using JQL (Jira Query Language).

    Example JQL queries:
      - project = MYPROJ AND status = "In Progress"
      - assignee = currentUser() ORDER BY updated DESC
      - sprint in openSprints() AND status != Done
      - labels = backend AND priority in (High, Highest)

    Args:
        jql: A valid JQL query string.
        max_results: Maximum number of results to return (default 20, max 50).
    """
    data = await jira().search_issues(jql, max_results=min(max_results, 50))
    issues = data.get("issues", [])
    total = data.get("total", 0)

    if not issues:
        return f"No issues found for JQL: `{jql}`"

    header = [
        f"### Search Results ({len(issues)} of {total} total)",
        "",
        "| Key | Summary | Status | Priority | Assignee |",
        "|-----|---------|--------|----------|----------|",
    ]
    rows = [_fmt_issue_row(i) for i in issues]
    return "\n".join(header + rows)


# ── Create Issue ────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_create_issue(
    project_key: str,
    summary: str,
    issue_type: str = "Task",
    description: str = "",
    assignee: str = "",
    priority: str = "",
    labels: str = "",
) -> str:
    """
    Create a new Jira issue.

    Args:
        project_key: The project key (e.g. "PROJ").
        summary: Issue title / summary.
        issue_type: Type of issue — Task, Bug, Story, Epic, Sub-task, etc.
        description: Detailed description (plain text).
        assignee: Username or account ID of the assignee (optional).
        priority: Priority name — Highest, High, Medium, Low, Lowest (optional).
        labels: Comma-separated labels (optional).
    """
    label_list = [l.strip() for l in labels.split(",") if l.strip()] if labels else None
    result = await jira().create_issue(
        project_key=project_key,
        summary=summary,
        issue_type=issue_type,
        description=description or None,
        assignee=assignee or None,
        priority=priority or None,
        labels=label_list,
    )
    key = result.get("key", "unknown")
    return f"✅ Issue **{key}** created successfully.\n\nLink: {JIRA_URL}/browse/{key}"


# ── Update Issue ────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_update_issue(
    issue_key: str,
    summary: str = "",
    description: str = "",
    priority: str = "",
    labels: str = "",
    assignee: str = "",
) -> str:
    """
    Update fields on an existing Jira issue. Only provided (non-empty) fields
    will be changed.

    Args:
        issue_key: The issue key (e.g. PROJ-123).
        summary: New summary / title (optional).
        description: New description (optional).
        priority: New priority name (optional).
        labels: Comma-separated labels — replaces existing labels (optional).
        assignee: New assignee username or account ID (optional).
    """
    fields: dict[str, Any] = {}
    if summary:
        fields["summary"] = summary
    if description:
        fields["description"] = description
    if priority:
        fields["priority"] = {"name": priority}
    if labels:
        fields["labels"] = [l.strip() for l in labels.split(",") if l.strip()]
    if assignee:
        fields["assignee"] = {"name": assignee}

    if not fields:
        return "⚠️ No fields provided to update."

    await jira().update_issue(issue_key, fields)
    updated = ", ".join(fields.keys())
    return f"✅ Issue **{issue_key}** updated: {updated}"


# ── Delete Issue ────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_delete_issue(issue_key: str) -> str:
    """
    Delete a Jira issue. This action is irreversible.

    Args:
        issue_key: The issue key to delete (e.g. PROJ-456).
    """
    await jira().delete_issue(issue_key)
    return f"🗑️ Issue **{issue_key}** has been deleted."


# ── Transitions ─────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_get_transitions(issue_key: str) -> str:
    """
    List available workflow transitions for an issue.
    Use this to discover valid transition IDs before calling jira_transition_issue.

    Args:
        issue_key: The issue key (e.g. PROJ-123).
    """
    transitions = await jira().get_transitions(issue_key)
    if not transitions:
        return f"No transitions available for {issue_key}."

    header = [
        f"### Available Transitions for {issue_key}",
        "",
        "| ID | Name | Target Status |",
        "|----|------|---------------|",
    ]
    rows = []
    for t in transitions:
        tid = t.get("id", "?")
        name = t.get("name", "—")
        target = (t.get("to") or {}).get("name", "—")
        rows.append(f"| {tid} | {name} | {target} |")

    return "\n".join(header + rows)


@mcp.tool()
async def jira_transition_issue(
    issue_key: str,
    transition_id: str,
    comment: str = "",
) -> str:
    """
    Move an issue through a workflow transition (change its status).

    First use jira_get_transitions to find the right transition ID.

    Args:
        issue_key: The issue key (e.g. PROJ-123).
        transition_id: The numeric transition ID (from jira_get_transitions).
        comment: Optional comment to add with the transition.
    """
    await jira().transition_issue(issue_key, transition_id, comment or None)
    return f"✅ Issue **{issue_key}** transitioned (transition ID: {transition_id})."


# ── Comments ────────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_get_comments(issue_key: str) -> str:
    """
    Fetch all comments on a Jira issue.

    Args:
        issue_key: The issue key (e.g. PROJ-123).
    """
    comments = await jira().get_comments(issue_key)
    if not comments:
        return f"No comments on {issue_key}."

    lines = [f"### Comments on {issue_key}", ""]
    for c in comments:
        author = (c.get("author") or {}).get("displayName", "Unknown")
        created = c.get("created", "—")
        body = c.get("body", "")[:500]
        lines += [
            f"**{author}** — {created}",
            f"> {body}",
            "",
        ]
    return "\n".join(lines)


@mcp.tool()
async def jira_add_comment(issue_key: str, comment: str) -> str:
    """
    Add a comment to a Jira issue.

    Args:
        issue_key: The issue key (e.g. PROJ-123).
        comment: The comment text to add.
    """
    await jira().add_comment(issue_key, comment)
    return f"✅ Comment added to **{issue_key}**."


# ── Assign Issue ────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_assign_issue(
    issue_key: str,
    account_id: str = "",
    username: str = "",
) -> str:
    """
    Assign (or unassign) a Jira issue.

    For Jira Cloud: use account_id.
    For Jira Server: use username.
    If both are empty, the issue is unassigned.

    Args:
        issue_key: The issue key (e.g. PROJ-123).
        account_id: Atlassian account ID (Cloud).
        username: Jira username (Server / Data Center).
    """
    await jira().assign_issue(
        issue_key,
        account_id=account_id or None,
        username=username or None,
    )
    who = account_id or username or "nobody (unassigned)"
    return f"✅ **{issue_key}** assigned to {who}."


# ── Projects ────────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_list_projects() -> str:
    """
    List all Jira projects visible to the authenticated user.
    """
    projects = await jira().list_projects()
    if not projects:
        return "No projects found."

    header = [
        "### Jira Projects",
        "",
        "| Key | Name | Type |",
        "|-----|------|------|",
    ]
    rows = []
    for p in projects:
        key = p.get("key", "?")
        name = p.get("name", "—")
        ptype = p.get("projectTypeKey", "—")
        rows.append(f"| {key} | {name} | {ptype} |")

    return "\n".join(header + rows)


# ── Boards ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_get_boards(project_key: str = "") -> str:
    """
    List agile boards, optionally filtered by project key.

    Args:
        project_key: Filter boards by project (optional).
    """
    boards = await jira().get_boards(project_key or None)
    if not boards:
        return "No boards found."

    header = [
        "### Agile Boards",
        "",
        "| ID | Name | Type |",
        "|----|------|------|",
    ]
    rows = []
    for b in boards:
        bid = b.get("id", "?")
        name = b.get("name", "—")
        btype = b.get("type", "—")
        rows.append(f"| {bid} | {name} | {btype} |")

    return "\n".join(header + rows)


# ── Sprints ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_get_sprints(board_id: int, state: str = "active") -> str:
    """
    List sprints for an agile board.

    Args:
        board_id: The board ID (get from jira_get_boards).
        state: Sprint state filter — "active", "future", or "closed".
    """
    sprints = await jira().get_sprints(board_id, state)
    if not sprints:
        return f"No {state} sprints found for board {board_id}."

    header = [
        f"### Sprints (board {board_id}, state={state})",
        "",
        "| ID | Name | State | Start | End |",
        "|----|------|-------|-------|-----|",
    ]
    rows = []
    for s in sprints:
        sid = s.get("id", "?")
        name = s.get("name", "—")
        sstate = s.get("state", "—")
        start = s.get("startDate", "—")[:10] if s.get("startDate") else "—"
        end = s.get("endDate", "—")[:10] if s.get("endDate") else "—"
        rows.append(f"| {sid} | {name} | {sstate} | {start} | {end} |")

    return "\n".join(header + rows)


@mcp.tool()
async def jira_get_sprint_issues(sprint_id: int) -> str:
    """
    List all issues in a specific sprint.

    Args:
        sprint_id: The sprint ID (get from jira_get_sprints).
    """
    issues = await jira().get_sprint_issues(sprint_id)
    if not issues:
        return f"No issues in sprint {sprint_id}."

    header = [
        f"### Issues in Sprint {sprint_id}",
        "",
        "| Key | Summary | Status | Priority | Assignee |",
        "|-----|---------|--------|----------|----------|",
    ]
    rows = [_fmt_issue_row(i) for i in issues]
    return "\n".join(header + rows)


# ── Who Am I ────────────────────────────────────────────────────────────────

@mcp.tool()
async def jira_whoami() -> str:
    """
    Show the currently authenticated Jira user's profile information.
    Useful to verify the connection is working.
    """
    me = await jira().get_myself()
    name = me.get("displayName", "—")
    email = me.get("emailAddress", "—")
    account_id = me.get("accountId", me.get("key", "—"))
    active = me.get("active", False)
    tz = me.get("timeZone", "—")

    return "\n".join([
        "### Authenticated User",
        "",
        f"| Field        | Value               |",
        f"|--------------|---------------------|",
        f"| **Name**     | {name}              |",
        f"| **Email**    | {email}             |",
        f"| **Account**  | {account_id}        |",
        f"| **Active**   | {'✅' if active else '❌'} |",
        f"| **Timezone** | {tz}                |",
    ])


# ═══════════════════════════════════════════════════════════════════════════
#  Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    print(f"Starting Jira MCP Server (transport={transport})...", file=sys.stderr)
    mcp.run(transport=transport)
