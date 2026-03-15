import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time
from typing import Any


class StdioJsonRpcClient:
    def __init__(self, command: list[str]):
        self.command = command
        self.proc: subprocess.Popen[str] | None = None
        self._messages: "queue.Queue[dict[str, Any]]" = queue.Queue()

    def start(self) -> None:
        self.proc = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stdout(self) -> None:
        assert self.proc is not None and self.proc.stdout is not None
        for raw in self.proc.stdout:
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                if isinstance(payload, dict):
                    self._messages.put(payload)
            except json.JSONDecodeError:
                continue

    def _read_stderr(self) -> None:
        assert self.proc is not None and self.proc.stderr is not None
        for raw in self.proc.stderr:
            line = raw.rstrip("\n")
            if line:
                print(f"[server] {line}", file=sys.stderr)

    def request(self, method: str, params: dict[str, Any], timeout: float = 25.0) -> dict[str, Any]:
        assert self.proc is not None and self.proc.stdin is not None
        request_id = int(time.time() * 1000)
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

        deadline = time.time() + timeout
        while time.time() < deadline:
            remaining = max(0.05, deadline - time.time())
            try:
                msg = self._messages.get(timeout=remaining)
            except queue.Empty as exc:
                raise TimeoutError(f"Timed out waiting for response to {method}") from exc

            if msg.get("id") == request_id:
                if "error" in msg:
                    raise RuntimeError(f"{method} failed: {json.dumps(msg['error'], indent=2)}")
                return msg
        raise TimeoutError(f"Timed out waiting for response to {method}")

    def stop(self) -> None:
        if not self.proc:
            return
        if self.proc.stdin:
            self.proc.stdin.close()
        try:
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except Exception:
            self.proc.kill()


def build_server_command(token_env_var: str, toolsets: str) -> list[str]:
    return [
        "docker",
        "run",
        "-i",
        "--rm",
        "-e",
        token_env_var,
        "-e",
        f"GITHUB_TOOLSETS={toolsets}",
        "-e",
        "GITHUB_READ_ONLY=1",
        "ghcr.io/github/github-mcp-server",
    ]


def initialize(client: StdioJsonRpcClient) -> None:
    params = {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "python-github-mcp-sample", "version": "1.0.0"},
    }
    _ = client.request("initialize", params)


def list_tools(client: StdioJsonRpcClient) -> list[dict[str, Any]]:
    response = client.request("tools/list", {})
    tools = response.get("result", {}).get("tools", [])
    if not isinstance(tools, list):
        return []
    return [t for t in tools if isinstance(t, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Python sample client for GitHub MCP Server")
    parser.add_argument(
        "--token-env-var",
        default="GITHUB_PERSONAL_ACCESS_TOKEN",
        help="Name of env var containing GitHub PAT",
    )
    parser.add_argument(
        "--toolsets",
        default="issues",
        help="GitHub MCP toolsets to enable (comma-separated), e.g. issues,pull_requests",
    )
    parser.add_argument(
        "--call-tool",
        default="",
        help="Optional tool name to call after listing tools",
    )
    parser.add_argument(
        "--tool-args",
        default="{}",
        help="JSON object string for the selected tool arguments",
    )

    args = parser.parse_args()

    if not os.getenv(args.token_env_var):
        print(
            f"Missing environment variable: {args.token_env_var}. "
            "Set it to a GitHub PAT before running.",
            file=sys.stderr,
        )
        return 1

    command = build_server_command(args.token_env_var, args.toolsets)
    client = StdioJsonRpcClient(command)

    try:
        client.start()
        initialize(client)

        tools = list_tools(client)
        print("Available tools:")
        for tool in tools:
            name = tool.get("name", "<unknown>")
            description = tool.get("description", "")
            print(f"- {name}: {description}")

        if args.call_tool:
            try:
                tool_args = json.loads(args.tool_args)
                if not isinstance(tool_args, dict):
                    raise ValueError("tool args must be a JSON object")
            except Exception as exc:
                print(f"Invalid --tool-args JSON: {exc}", file=sys.stderr)
                return 2

            response = client.request(
                "tools/call",
                {"name": args.call_tool, "arguments": tool_args},
                timeout=45.0,
            )
            print("\nTool call result:")
            print(json.dumps(response.get("result", {}), indent=2))

    except FileNotFoundError:
        print("Docker command not found. Install Docker Desktop and retry.", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 4
    finally:
        client.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
