"""
Unit Tests for Ollama Client
Tests context engineering, embeddings, and structured output.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.ollama.client import OllamaClient, ToolDefinition


@pytest.fixture
async def ollama_client():
    """Fixture for Ollama client."""
    client = OllamaClient(
        base_url="http://localhost:11434",
        model="mistral"
    )
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_ollama_initialization():
    """Test Ollama client initialization."""
    client = OllamaClient(
        base_url="http://localhost:11434",
        model="mistral"
    )
    assert client.model == "mistral"
    assert client.base_url == "http://localhost:11434"
    await client.close()


@pytest.mark.asyncio
async def test_generate_with_system_prompt(ollama_client):
    """Test generation with system prompt (context engineering)."""
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is Python?"

    with patch.object(ollama_client, '_request') as mock_request:
        mock_request.return_value = {
            "message": {"content": "Python is a programming language."}
        }

        response = await ollama_client.generate_with_context(
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )

        assert response == "Python is a programming language."
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_generate_with_tools(ollama_client):
    """Test generation with tools (context engineering)."""
    tools = [
        ToolDefinition(
            name="search_web",
            description="Search the web",
            parameters={"query": "string"}
        )
    ]

    with patch.object(ollama_client, '_request') as mock_request:
        mock_request.return_value = {
            "message": {"content": "I'll search for that information."}
        }

        response = await ollama_client.generate_with_context(
            user_prompt="Find information about AI",
            tools=tools
        )

        assert response == "I'll search for that information."


@pytest.mark.asyncio
async def test_structured_output(ollama_client):
    """Test structured JSON output from LLM."""
    with patch.object(ollama_client, '_request') as mock_request:
        mock_request.return_value = {
            "message": {"content": '{"summary": "Test summary", "confidence": 0.9}'}
        }

        result = await ollama_client.analyze_with_structured_output(
            content="Test content",
            analysis_task="Analyze this"
        )

        assert result["summary"] == "Test summary"
        assert result["confidence"] == 0.9


@pytest.mark.asyncio
async def test_embedding_generation(ollama_client):
    """Test embedding generation for RAG."""
    with patch.object(ollama_client, '_request') as mock_request:
        mock_request.return_value = {
            "embedding": [0.1, 0.2, 0.3, 0.4]
        }

        embedding = await ollama_client.generate_embedding("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 4


@pytest.mark.asyncio
async def test_health_check(ollama_client):
    """Test Ollama health check."""
    with patch.object(ollama_client, '_request') as mock_request:
        mock_request.return_value = {"models": []}

        health = await ollama_client.check_health()

        assert health is True


@pytest.mark.asyncio
async def test_health_check_failure(ollama_client):
    """Test Ollama health check when service is down."""
    with patch.object(ollama_client, '_request', side_effect=Exception("Connection refused")):
        health = await ollama_client.check_health()
        assert health is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])