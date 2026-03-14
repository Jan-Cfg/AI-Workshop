### Model Context Protocol
Model Context Protocol is a open protocol used between the AI agent and backend application/service. MCP server represents the backend application/services in this MCP architecture and an MCP client is a piece of code that communicates with the MCP server.

### MCP Server
As a example, I have used a Database MCP server for my use-case which is **Mortgage Partial Pre-payment functionality**. So a simple Database MCP server that have the capability to list databases, list connections and execute queries.

A simple piece of javascript code is used as the MCP client that consumes the Database MCP server and calls the tools provided by the MCP server.

**MCP Server:** [MCP Database Server](https://mcpservers.org/en/servers/ahmetbarut/mcp-database-server)

