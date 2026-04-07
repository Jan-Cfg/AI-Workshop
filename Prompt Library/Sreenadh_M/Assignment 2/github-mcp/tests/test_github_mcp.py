import json
import pytest
from github_mcp_server import (
    list_repositories,
    get_repository,
    get_user_profile,
    create_issue,
    TOOLS,
)

class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)

    def json(self):
        return self._payload


class MockAsyncClient:
    response = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def get(self, *args, **kwargs):
        return MockAsyncClient.response

    async def post(self, *args, **kwargs):
        return MockAsyncClient.response


@pytest.fixture(autouse=True)
def patch_httpx_client(monkeypatch):
    import github_mcp_server
    monkeypatch.setattr(github_mcp_server.httpx, "AsyncClient", MockAsyncClient)


@pytest.mark.asyncio
async def test_list_repositories_returns_expected_json():
    MockAsyncClient.response = DummyResponse(200, [{"name": "repo1", "html_url": "https://github.com/example/repo1", "stargazers_count": 10}])
    result = await list_repositories("example")
    data = json.loads(result)
    assert isinstance(data, list)
    assert data[0]["name"] == "repo1"
    assert data[0]["stars"] == 10


@pytest.mark.asyncio
async def test_get_repository_returns_parsed_reference():
    payload = {
        "name": "demo",
        "description": "Demo repo",
        "html_url": "https://github.com/example/demo",
        "stargazers_count": 3,
        "forks_count": 1,
        "language": "Python",
        "open_issues_count": 0,
    }
    MockAsyncClient.response = DummyResponse(200, payload)
    result = await get_repository("example", "demo")
    data = json.loads(result)
    assert data["name"] == "demo"
    assert data["language"] == "Python"
    assert data["open_issues"] == 0


@pytest.mark.asyncio
async def test_get_user_profile_returns_user_info():
    payload = {
        "name": "Example User",
        "bio": "Example bio",
        "company": "Example Inc",
        "location": "Earth",
        "public_repos": 5,
        "followers": 10,
        "following": 2,
    }
    MockAsyncClient.response = DummyResponse(200, payload)
    result = await get_user_profile("example")
    data = json.loads(result)
    assert data["name"] == "Example User"
    assert data["company"] == "Example Inc"
    assert data["followers"] == 10


@pytest.mark.asyncio
async def test_create_issue_returns_issue_reference():
    payload = {
        "number": 123,
        "title": "Bug report",
        "html_url": "https://github.com/example/repo/issues/123",
    }
    MockAsyncClient.response = DummyResponse(201, payload)
    result = await create_issue("example", "repo", "Bug report", "Please fix this")
    data = json.loads(result)
    assert data["number"] == 123
    assert data["title"] == "Bug report"
    assert data["url"] == "https://github.com/example/repo/issues/123"


def test_tool_list_contains_expected_names():
    names = [tool.name for tool in TOOLS]
    assert "list_repositories" in names
    assert "get_repository" in names
    assert "get_user_profile" in names
    assert "create_issue" in names
