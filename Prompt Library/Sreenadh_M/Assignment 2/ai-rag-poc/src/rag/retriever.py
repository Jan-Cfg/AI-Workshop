"""
Document Retriever Component of RAG Pipeline
Handles similarity search in vector database.
"""
from typing import Optional


class Retriever:
    """Retrieves relevant documents from vector store."""

    def __init__(self, vector_db, embedding_client, top_k: int = 5, threshold: float = 0.7):
        self.vector_db = vector_db
        self.embedding_client = embedding_client
        self.top_k = top_k
        self.threshold = threshold

    async def retrieve(self, query: str) -> list[dict]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User query string

        Returns:
            List of relevant documents with similarity scores
        """
        # Generate embedding for query
        query_embedding = await self.embedding_client.generate_embedding(query)

        if not query_embedding:
            return []

        # Search vector database
        results = await self.vector_db.similarity_search(
            query_embedding=query_embedding,
            limit=self.top_k,
            threshold=self.threshold,
        )

        return results

    async def retrieve_by_document_id(self, doc_id: int) -> dict:
        """Retrieve specific document by ID."""
        return await self.vector_db.get_document(doc_id)

    async def get_all_processed_documents(self) -> list[dict]:
        """Get all documents in knowledge base."""
        return await self.vector_db.list_documents(processed_only=True)
        
        return documents