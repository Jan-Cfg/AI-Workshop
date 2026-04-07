"""
Response Generator Component of RAG Pipeline
Generates responses using retrieved context and LLM.
"""
from typing import Optional


class Generator:
    """Generates responses using LLM with retrieved context."""

    def __init__(self, ollama_client, system_prompt: Optional[str] = None):
        self.ollama_client = ollama_client
        self.system_prompt = system_prompt or """You are a helpful assistant that answers questions 
based on provided context and documents. Always cite sources when referencing documents. 
If the answer cannot be found in the context, say so explicitly."""

    async def generate_response(
        self,
        query: str,
        context_documents: list[dict],
        temperature: float = 0.5,
    ) -> str:
        """
        Generate response using context from retrieved documents.

        Args:
            query: User query
            context_documents: Retrieved documents from vector DB
            temperature: Model temperature

        Returns:
            Generated response text
        """

        # Format context
        context_text = self._format_context(context_documents)

        # Build user prompt with context
        user_prompt = f"""Based on the following context, please answer: {query}

CONTEXT:
{context_text if context_text else 'No relevant documents found.'}"""

        # Generate response
        response = await self.ollama_client.generate_with_context(
            user_prompt=user_prompt,
            system_prompt=self.system_prompt,
            temperature=temperature,
        )

        return response

    @staticmethod
    def _format_context(documents: list[dict]) -> str:
        """Format retrieved documents into context string."""
        if not documents:
            return ""

        context_parts = []
        for doc in documents:
            similarity = doc.get("similarity", 0.0)
            filename = doc.get("filename", "Unknown")
            chunk = doc.get("chunk_text", "")

            context_parts.append(
                f"[{filename} - Relevance: {similarity:.0%}]\n{chunk[:500]}..."
            )

        return "\n---\n".join(context_parts)

    async def generate_summary(
        self,
        documents: list[dict],
    ) -> str:
        """Generate summary from multiple documents."""
        context = self._format_context(documents)

        prompt = f"""Please provide a comprehensive summary of the following documents:

{context}

Focus on key points and insights."""

        return await self.ollama_client.generate_with_context(
            user_prompt=prompt,
            system_prompt="You are a summarization expert. Provide clear, concise summaries.",
            temperature=0.3,
        )