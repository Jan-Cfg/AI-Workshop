# 🛠️ Model Context Protocol (MCP) ADO.NET Server

This C# Console Application is an official **MCP Server** implementation pattern designed to integrate with AI agents (like Claude Desktop or the MCP Inspector) to programmatically write, run, and update ADO.NET Unit Tests using `Moq`.

## 📦 Project Overview

The project relies on three key nuget dependencies natively integrated inside `McpAdoNetServer.csproj`:
* `ModelContextProtocol`: The official C# MCP SDK community release.
* `Microsoft.Extensions.Hosting`: Used for setting up DI and configuration blocks required by MCP Servers.
* `Moq` & `NUnit`: Used by generated C# scripts for compiling database mocks (`IDbConnection`, `IDbCommand`, `IDataReader`).

---

## 🏗️ Architecture

The MCP Server exposes tool actions to Large Language Models leveraging the `McpAdoNetUnitTestAssistant.cs` logic.

### 1. `McpAdoNetUnitTestAssistant.cs`
This class handles all the functional operations:
* **`WriteAdoNetUnitTestAsync(className, code)`**: Saves AI-generated Moq setups locally.
* **`ExecuteUnitTestsAsync()`**: Spawns a background `dotnet test` process, reading `StandardOutput` to verify if the LLM's test passed or failed.
* **`UpdateFailingTestAsync()`**: Updates broken tests based on the error output.

### 2. `Program.cs` (MCP Registration)
The main entry point binds the assistant logic to standard MCP Tool Protocol formats so an LLM client understands how to invoke them via `stdio`.

**Sample Code for MCP Integration:**
```csharp
var builder = Host.CreateApplicationBuilder(args);

// Register application logic
var testAssistant = new McpAdoNetUnitTestAssistant(@"C:\repos\MySharedSolution\MyTests");
builder.Services.AddSingleton(testAssistant);

// Register MCP Tools
builder.Services.AddMcpServer(options =>
{
    options.ServerInfo = new Implementation { Name = "AdoNetTestServer", Version = "1.0.0" };

    options.AddTool(
        name: "execute_unit_tests",
        description: "Executes unit tests and returns failure data if any.",
        inputSchema: new { type = "object", properties = new { specificTestClass = new { type = "string" } } },
        handler: async (request, cancellationToken) =>
        {
            string result = await testAssistant.ExecuteUnitTestsAsync();
            return new CallToolResult { Content = { new TextContent(result) } };
        });
});

var app = builder.Build();
await app.RunAsync();
```

---

## 🧪 Testing the Server Locally

MCP strictly communicates over Standard Input/Output. **Do not just double click the .exe**, it requires a dedicated JSON-RPC Client.

### Option 1: Using the Official MCP Inspector (CLI UI)
Use the `@modelcontextprotocol/inspector` node module. It provides a browser UI to manually invoke your tools and ensure they work without spinning up an LLM. 
*(Requires Node.js)*

```bash
# Run this command in your terminal
npx @modelcontextprotocol/inspector dotnet run --project .\McpAdoNetServer.csproj
```
Wait for the terminal to print a local URL (e.g. `http://localhost:5173`), open it, and click "Connect". Your tools will appear!

### Option 2: Full Integration with Claude Desktop
To actually test it dynamically via AI Chat prompts, register your local project inside Claude Desktop's config file (usually located at `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "AdoNetUnitTester": {
      "command": "dotnet",
      "args": [
        "run",
        "--project",
        "C:\\Users\\smahajan.ctr\\source\\repos\\MySharedSolution\\mcp\\McpAdoNetServer\\McpAdoNetServer.csproj"
      ]
    }
  }
}
```
Restart Claude, click the **⚒️ (Plug/Hammer Icon)**, and explicitly ask Claude: *"Please write a mock ADO.NET test for EmployeeCRUD using the AdoNetUnitTester tools attached to you."*
