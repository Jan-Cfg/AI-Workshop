"""
Unit Tests for RAG Pipeline
Tests retriever, generator, and 4-step document enrichment.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.rag.retriever import Retriever
from src.rag.generator import Generator
from src.utils.document_processor import DocumentProcessor


@pytest.fixture
def mock_vector_db():
    """Mock vector database."""
    mock_db = MagicMock()
    mock_db.similarity_search = AsyncMock()
    mock_db.store_document = AsyncMock()
    mock_db.store_embedding = AsyncMock()
    mock_db.mark_processed = AsyncMock()
    return mock_db


@pytest.fixture
def mock_ollama():
    """Mock Ollama client."""
    mock_ollama = MagicMock()
    mock_ollama.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
    mock_ollama.generate_with_context = AsyncMock(return_value="Generated response")
    return mock_ollama


@pytest.fixture
def retriever(mock_vector_db, mock_ollama):
    """Fixture for retriever."""
    return Retriever(
        vector_db=mock_vector_db,
        embedding_client=mock_ollama,
        top_k=5,
        threshold=0.7
    )


@pytest.fixture
def generator(mock_ollama):
    """Fixture for generator."""
    return Generator(ollama_client=mock_ollama)


@pytest.mark.asyncio
async def test_retriever_retrieve(retriever, mock_vector_db, mock_ollama):
    """Test document retrieval."""
    mock_vector_db.similarity_search.return_value = [
        {
            "filename": "doc1.txt",
            "chunk_text": "Sample text",
            "similarity": 0.95
        }
    ]

    results = await retriever.retrieve("test query")

    assert len(results) == 1
    assert results[0]["filename"] == "doc1.txt"
    mock_ollama.generate_embedding.assert_called_once()


@pytest.mark.asyncio
async def test_retriever_empty_results(retriever, mock_vector_db, mock_ollama):
    """Test retriever with no results."""
    mock_vector_db.similarity_search.return_value = []

    results = await retriever.retrieve("nonexistent query")

    assert len(results) == 0


@pytest.mark.asyncio
async def test_generator_response(generator, mock_ollama):
    """Test response generation."""
    documents = [
        {"filename": "doc.txt", "chunk_text": "Some content", "similarity": 0.9}
    ]

    response = await generator.generate_response(
        query="What is in this document?",
        context_documents=documents
    )

    assert response == "Generated response"
    mock_ollama.generate_with_context.assert_called_once()


@pytest.mark.asyncio
async def test_generator_no_documents(generator, mock_ollama):
    """Test generator with no documents."""
    response = await generator.generate_response(
        query="test query",
        context_documents=[]
    )

    assert response == "Generated response"


@pytest.mark.asyncio
async def test_document_processor_chunking():
    """Test document chunking."""
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=10)

    text = "Sentence one. " * 20  # Create large text
    chunks = processor.chunk_document(text)

    assert len(chunks) > 0
    assert all(len(chunk) <= 150 for chunk in chunks)  # Allow some overlap


@pytest.mark.asyncio
async def test_full_rag_pipeline(mock_vector_db, mock_ollama):
    """Test full RAG enrichment pipeline."""
    processor = DocumentProcessor()

    mock_vector_db.store_document.return_value = 1
    mock_vector_db.store_embedding.return_value = 1

    # Create temp test file
    test_content = "This is a test document with some sample content."
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        result = await processor.process_document_full_pipeline(
            file_path=temp_file,
            vector_db=mock_vector_db,
            ollama_client=mock_ollama
        )

        assert result["document_id"] == 1
        assert result["chunks"] > 0
        assert result["enrichment_stats"]["embeddings_stored"] >= 0

    finally:
        import os
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])