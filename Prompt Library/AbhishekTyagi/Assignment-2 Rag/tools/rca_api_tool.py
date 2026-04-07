from langchain.tools import tool
import requests

API_BASE_URL = "http://localhost:8080"

@tool
def call_rca_api(action: str) -> str:
    """
    Call RCA APIs.
    Supported actions:
      - list_failed
    """
    if action == "list_failed":
        return requests.get(
            f"{API_BASE_URL}/api/rca/policies/failed"
        ).json()

    return "Unsupported API action"