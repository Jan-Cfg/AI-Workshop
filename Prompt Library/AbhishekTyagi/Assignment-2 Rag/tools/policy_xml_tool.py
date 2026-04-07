from langchain.tools import tool
import os

XML_FOLDER = "C:/policies/generated"

@tool
def read_policy_xml(policy_name: str) -> str:
    """
    Read policy XML from C:/policies/generated.
    """
    path = f"{XML_FOLDER}/{policy_name}.xml"
    if not os.path.exists(path):
        return f"XML NOT FOUND at {path}"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()