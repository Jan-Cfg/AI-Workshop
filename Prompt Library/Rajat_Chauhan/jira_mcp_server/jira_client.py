import base64
from typing import Any

import httpx


class JiraClient:

    # ── Construction ────────────────────────────────────────────────────────

    def __init__(self, base_url: str, email: str, api_token: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._auth_header = self._build_auth_header(email, api_token)
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": self._auth_header,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    # ── Auth helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _build_auth_header(email: str, token: str) -> str:
        creds = f"{email}:{token}"
        encoded = base64.b64encode(creds.encode()).decode()
        return f"Basic {encoded}"

    # ── Low-level HTTP ──────────────────────────────────────────────────────

    async def _request(self, method: str, path: str, **kwargs) -> dict | list | None:
        resp = await self._client.request(method, path, **kwargs)
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    async def _get(self, path: str, params: dict | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def _post(self, path: str, json: dict | None = None) -> Any:
        return await self._request("POST", path, json=json)

    async def _put(self, path: str, json: dict | None = None) -> Any:
        return await self._request("PUT", path, json=json)

    async def _delete(self, path: str) -> Any:
        return await self._request("DELETE", path)

    # ═══════════════════════════════════════════════════════════════════════
    #  ISSUES
    # ═══════════════════════════════════════════════════════════════════════

    async def get_issue(self, issue_key: str, fields: str | None = None) -> dict:
        """Fetch a single issue by key (e.g. PROJ-123)."""
        params = {}
        if fields:
            params["fields"] = fields
        return await self._get(f"/rest/api/2/issue/{issue_key}", params=params)

    async def search_issues(
        self,
        jql: str,
        max_results: int = 50,
        start_at: int = 0,
        fields: str | None = None,
    ) -> dict:
        """Search for issues using JQL."""
        body: dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
        }
        if fields:
            body["fields"] = [f.strip() for f in fields.split(",")]
        return await self._post("/rest/api/2/search", json=body)

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: str | None = None,
        assignee: str | None = None,
        priority: str | None = None,
        labels: list[str] | None = None,
        extra_fields: dict | None = None,
    ) -> dict:
        """Create a new Jira issue."""
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            fields["description"] = description
        if assignee:
            fields["assignee"] = {"name": assignee}
        if priority:
            fields["priority"] = {"name": priority}
        if labels:
            fields["labels"] = labels
        if extra_fields:
            fields.update(extra_fields)

        return await self._post("/rest/api/2/issue", json={"fields": fields})

    async def update_issue(self, issue_key: str, fields: dict) -> None:
        """Update fields on an existing issue."""
        await self._put(f"/rest/api/2/issue/{issue_key}", json={"fields": fields})

    async def delete_issue(self, issue_key: str) -> None:
        """Delete an issue by key."""
        await self._delete(f"/rest/api/2/issue/{issue_key}")

    # ═══════════════════════════════════════════════════════════════════════
    #  TRANSITIONS  (status changes)
    # ═══════════════════════════════════════════════════════════════════════

    async def get_transitions(self, issue_key: str) -> list[dict]:
        """Return available workflow transitions for an issue."""
        data = await self._get(f"/rest/api/2/issue/{issue_key}/transitions")
        return data.get("transitions", [])

    async def transition_issue(
        self, issue_key: str, transition_id: str, comment: str | None = None
    ) -> None:
        """Move an issue through a workflow transition (change status)."""
        body: dict[str, Any] = {"transition": {"id": transition_id}}
        if comment:
            body["update"] = {
                "comment": [{"add": {"body": comment}}]
            }
        await self._post(f"/rest/api/2/issue/{issue_key}/transitions", json=body)

    # ═══════════════════════════════════════════════════════════════════════
    #  COMMENTS
    # ═══════════════════════════════════════════════════════════════════════

    async def get_comments(self, issue_key: str) -> list[dict]:
        """Fetch all comments on an issue."""
        data = await self._get(f"/rest/api/2/issue/{issue_key}/comment")
        return data.get("comments", [])

    async def add_comment(self, issue_key: str, body: str) -> dict:
        """Add a comment to an issue."""
        return await self._post(
            f"/rest/api/2/issue/{issue_key}/comment", json={"body": body}
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  PROJECTS
    # ═══════════════════════════════════════════════════════════════════════

    async def list_projects(self) -> list[dict]:
        """List all projects visible to the authenticated user."""
        return await self._get("/rest/api/2/project")

    async def get_project(self, project_key: str) -> dict:
        """Get details of a single project."""
        return await self._get(f"/rest/api/2/project/{project_key}")

    # ═══════════════════════════════════════════════════════════════════════
    #  USERS
    # ═══════════════════════════════════════════════════════════════════════

    async def get_myself(self) -> dict:
        """Return the currently authenticated user profile."""
        return await self._get("/rest/api/2/myself")

    async def assign_issue(self, issue_key: str, account_id: str | None = None, username: str | None = None) -> None:
        """Assign an issue to a user (pass account_id for Cloud, username for Server)."""
        body: dict[str, Any] = {}
        if account_id:
            body["accountId"] = account_id
        elif username:
            body["name"] = username
        else:
            # unassign
            body["accountId"] = None
        await self._put(f"/rest/api/2/issue/{issue_key}/assignee", json=body)

    # ═══════════════════════════════════════════════════════════════════════
    #  SPRINTS  (Jira Software / Agile)
    # ═══════════════════════════════════════════════════════════════════════

    async def get_boards(self, project_key: str | None = None) -> list[dict]:
        """List agile boards, optionally filtered by project."""
        params = {}
        if project_key:
            params["projectKeyOrId"] = project_key
        data = await self._get("/rest/agile/1.0/board", params=params)
        return data.get("values", [])

    async def get_sprints(self, board_id: int, state: str = "active") -> list[dict]:
        """List sprints for a board (state: active, future, closed)."""
        data = await self._get(
            f"/rest/agile/1.0/board/{board_id}/sprint",
            params={"state": state},
        )
        return data.get("values", [])

    async def get_sprint_issues(self, sprint_id: int) -> list[dict]:
        """List issues in a sprint."""
        data = await self._get(f"/rest/agile/1.0/sprint/{sprint_id}/issue")
        return data.get("issues", [])
