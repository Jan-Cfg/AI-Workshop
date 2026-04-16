import { spawn } from "child_process";

const mcpServer = spawn("npx", ["-y", "@ahmetbarut/mcp-database-server"]);

mcpServer.stdout.on("data", (data) => {
    console.log("MCP Server:", data.toString());
});

mcpServer.stderr.on("data", (data) => {
    console.error("Error:", data.toString());
});

function sendRequest(method, params) {
    const request = {
        jsonrpc: "2.0",
        id: Date.now(),
        method: method,
        params: params
    };

    mcpServer.stdin.write(JSON.stringify(request) + "\n");
}

// list database connections
sendRequest("tools/call", {
    name: "list_connections",
    arguments: {
        include_credentials: false
    }
});

// execute a SQL query
sendRequest("tools/call", {
    name: "execute_query",
    arguments: {
        connection_name: "mysql",
        query: "SELECT balance FROM customers WHERE customerId='001059'",
        parameters: []
    }
});