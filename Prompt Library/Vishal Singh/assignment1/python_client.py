import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client,StdioServerParameters


    
async def main():
    selected_tool = None  
    server_params = StdioServerParameters(
        command="docker",
        args=["run","-i","--rm","-e","GITHUB_PERSONAL_ACCESS_TOKEN=<Your PAT>",
              "ghcr.io/github/github-mcp-server:latest"]
    )

    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:

            await session.initialize()
            tools=await session.list_tools()
             
            result = await session.call_tool("list_commits",{
                "owner":"vsingh-107885",
                "repo" :"TestApp"
            })
            print(result)    
            
            


asyncio.run(main())            
