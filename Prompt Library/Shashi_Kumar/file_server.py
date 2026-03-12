import os
from mcp.server.fastmcp import FastMCP

# 1. Initialize the FastMCP server
mcp = FastMCP("LocalDataFetcher")

# 2. Define the tool to fetch file data
@mcp.tool()
def fetch_local_file_content(file_path: str) -> str:
    """
    Fetches and returns the text content of a local file.
    The AI will provide the 'file_path' argument.
    """
    # Security: Ensure the path exists and is a file
    if not os.path.isfile(file_path):
        return f"Error: The path '{file_path}' is not a valid file."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return f"--- Content of {file_path} ---\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

# 3. Start the server using stdio transport
if __name__ == "__main__":
    mcp.run()
