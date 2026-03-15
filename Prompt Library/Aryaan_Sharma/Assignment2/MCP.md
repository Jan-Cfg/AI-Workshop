# Overview

This project demonstrates a Test‑Repair MCP Server implemented in .NET using ASP.NET Core and the Model Context Protocol (MCP).

# The MCP server exposes:

1. Unit test execution (dotnet test)
2. Read access to code and test code
3. Write access to update unit tests
4. A guided prompt for repairing failing xUnit tests

The goal is to showcase how AI agents can repair failing unit tests after application behavior changes, using MCP as a standardized integration layer.

# Why MCP for Test Repair?

When business logic changes:

1. Unit tests often fail
2. Developers must update assertions or add new tests

MCP enables this workflow safely by:

1. Exposing test execution as tools
2. Exposing code as structured resources
3. Letting AI agents reason and act through controlled interfaces

MCP does not embed AI logic — it provides capabilities, not decisions.

# Project Structure

TestRepairMcpDemo/
│
├── Calculator/ # Production code
│ └── Calculator.cs
│
├── Calculator.Tests/ # xUnit tests
│ └── CalculatorTests.cs
│
├── TestRepairMcp/ # MCP Server
│ └── Program.cs

# Required NuGet Packages

1. dotnet add package ModelContextProtocol --version 1.1.0
2. dotnet add package ModelContextProtocol.AspNetCore --version 1.1.0

# MCP Server Code (Program.cs)

using System.Diagnostics;
using ModelContextProtocol.Server;
using ModelContextProtocol.AspNetCore;

var builder = WebApplication.CreateBuilder(args);

// Register MCP server with HTTP transport (Streamable HTTP)
builder.Services
.AddMcpServer()
.WithHttpTransport();

var app = builder.Build();

// Map MCP JSON‑RPC endpoint
app.MapMcp();

app.Run();

// ================= MCP TOOLS =================
public static class TestTools
{
[McpServerTool(Name = "run_tests", Title = "Runs all unit tests using dotnet test")]
public static string RunTests()
{
var psi = new ProcessStartInfo("dotnet", "test")
{
RedirectStandardOutput = true,
RedirectStandardError = true,
UseShellExecute = false
};

        using var process = Process.Start(psi)!;
        var output = process.StandardOutput.ReadToEnd();
        var error = process.StandardError.ReadToEnd();
        process.WaitForExit();

        return output + error;
    }

}

// ================= MCP RESOURCES =================
public static class SourceResources
{
[McpServerResource(UriTemplate = "file://src/{path}", MimeType = "text/plain")]
public static string ReadSource(string path)
{
return File.ReadAllText(Path.Combine("..", "..", "Calculator", path));
}
}

public static class TestResources
{
[McpServerResource(UriTemplate = "file://tests/{path}", MimeType = "text/plain")]
public static string ReadTest(string path)
{
return File.ReadAllText(Path.Combine("..", "..", "Calculator.Tests", path));
}
}

// ================= MCP TOOL – UPDATE TEST =================
public static class TestUpdateTool
{
[McpServerTool(Name = "update_test_file", Title = "Updates or creates an xUnit test file")]
public static void UpdateTestFile(string path, string content)
{
File.WriteAllText(Path.Combine("..", "..", "Calculator.Tests", path), content);
}
}

// ================= MCP PROMPT =================
public static class RepairPrompt
{
[McpServerPrompt(Name = "repair_xunit_tests", Title = "Guidelines for safely repairing failing xUnit tests")]
public static string Prompt() =>
"""
You are repairing failing xUnit tests.

Rules:

- Do NOT modify production code
- Update tests to reflect new behavior
- Preserve original test intent
- Keep assertions explicit
- Add new tests only if behavior expanded
  """;
  }

# Running the MCP Server

cd TestRepairMcpdotnet run

# The server starts on:

http://localhost:5000/

# Initilization Request

{
"jsonrpc": "2.0",
"id": 0,
"method": "initialize",
"params": {
"clientInfo": {
"name": "Postman",
"version": "1.0"
},
"protocolVersion": "2024-11-05"
}
}

# List request

{
"jsonrpc": "2.0",
"id": 1,
"method": "tools/list"
}

# Run test with suggestions by AI

{
"jsonrpc": "2.0",
"id": 2,
"method": "tools/call",
"params": {
"name": "run_tests",
"arguments": {}
}
}
