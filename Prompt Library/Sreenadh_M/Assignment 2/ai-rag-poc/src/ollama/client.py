"""
Ollama Client with Context Engineering
Demonstrates system prompts, user prompts, tools, and structured output.
"""
import json
from typing import Any, Optional
import httpx
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Tool schema for structured output."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: dict = Field(default_factory=dict, description="Tool parameters schema")


class OllamaClient:
    """
    Ollama client with context engineering capabilities.
    Supports system prompts, user prompts, tools, and structured output.
    """

    def __init__(self, base_url: str, model: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()

    async def _request(self, endpoint: str, **kwargs) -> dict:
        """Low-level HTTP request."""
        resp = await self._client.post(endpoint, **kwargs)
        resp.raise_for_status()
        return resp.json()

    # ════════════════════════════════════════════════════════════════════════
    # Context Engineering: System Prompts + User Prompts
    # ════════════════════════════════════════════════════════════════════════

    async def generate_with_context(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[list[ToolDefinition]] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate response with full context engineering.

        Args:
            user_prompt: The user's query
            system_prompt: System context/instructions
            tools: Optional list of available tools
            temperature: Model temperature (0.0-1.0)

        Returns:
            Generated response text
        """

        # Build messages with system context
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Add tool information to system context if provided
        if tools:
            tool_context = self._format_tools_for_context(tools)
            if messages and messages[0].get("role") == "system":
                messages[0]["content"] += f"\n\nAvailable Tools:\n{tool_context}"
            else:
                messages.insert(0, {
                    "role": "system",
                    "content": f"Available Tools:\n{tool_context}"
                })

        # User prompt
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        # Prepare request
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }

        response = await self._request("/api/chat", json=payload)
        
        if isinstance(response, dict):
            return response.get("message", {}).get("content", "")
        return ""

    # ════════════════════════════════════════════════════════════════════════
    # Structured Output: Tool Recommendations
    # ════════════════════════════════════════════════════════════════════════

    async def analyze_with_structured_output(
        self,
        content: str,
        analysis_task: str,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """
        Analyze content and return structured output as JSON.

        Returns:
            Parsed JSON response
        """

        default_system = system_prompt or """You are an expert analyzer.
Respond ONLY with valid JSON in this format:
{
    "summary": "brief summary",
    "key_insights": ["insight1", "insight2"],
    "sentiment": "positive|neutral|negative",
    "confidence": 0.0-1.0
}"""

        prompt = f"""{analysis_task}

Content:
{content[:2000]}

Respond ONLY with valid JSON."""

        response = await self.generate_with_context(
            user_prompt=prompt,
            system_prompt=default_system,
            temperature=0.3,  # Lower temperature for structured output
        )

        # Try to parse as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "summary": response,
                "key_insights": [],
                "sentiment": "neutral",
                "confidence": 0.0
            }

    # ════════════════════════════════════════════════════════════════════════
    # Embedding Generation (for RAG vectors)
    # ════════════════════════════════════════════════════════════════════════

    async def generate_embedding(self, text: str, model: Optional[str] = None) -> list[float]:
        """
        Generate embedding vector for text.
        Used for RAG similarity matching.

        Args:
            text: Text to embed
            model: Embedding model (defaults to main model)

        Returns:
            List of floats representing the embedding vector
        """
        model = model or self.model

        payload = {
            "model": model,
            "prompt": text,
        }

        response = await self._request("/api/embeddings", json=payload)

        if isinstance(response, dict):
            return response.get("embedding", [])
        return []

    # ════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _format_tools_for_context(tools: list[ToolDefinition]) -> str:
        """Format tools for inclusion in system context."""
        lines = []
        for tool in tools:
            lines.append(f"- {tool.name}: {tool.description}")
        return "\n".join(lines)

    async def check_health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = await self._request("/api/tags", json={})
            return response is not None
        except Exception:
            return False