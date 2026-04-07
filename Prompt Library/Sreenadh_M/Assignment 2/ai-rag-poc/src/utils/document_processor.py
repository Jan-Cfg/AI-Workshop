"""
4-Step RAG Document Enrichment Pipeline
1. Load document
2. Chunk document
3. Generate embeddings
4. Store in vector DB
"""
import hashlib
import re
from pathlib import Path
from typing import Optional, Tuple


class DocumentProcessor:
    """4-step RAG pipeline for document enrichment."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ════════════════════════════════════════════════════════════════════════
    # Step 1: Load Document
    # ════════════════════════════════════════════════════════════════════════

    async def load_document(self, file_path: str) -> Tuple[str, dict]:
        """
        Step 1: Load document from file.

        Returns:
            (content, metadata) tuple
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read content based on file type
        if path.suffix.lower() == ".pdf":
            content = await self._load_pdf(file_path)
        elif path.suffix.lower() in [".txt", ".md", ".markdown"]:
            content = path.read_text(encoding="utf-8")
        else:
            # Try to read as text
            content = path.read_text(encoding="utf-8")

        metadata = {
            "filename": path.name,
            "file_type": path.suffix,
            "file_size": path.stat().st_size,
            "content_hash": self._compute_hash(content),
        }

        return content, metadata

    @staticmethod
    async def _load_pdf(file_path: str) -> str:
        """Extract text from PDF."""
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join(page.extract_text() for page in reader.pages)
            return text
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {e}")

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    # ════════════════════════════════════════════════════════════════════════
    # Step 2: Chunk Document
    # ════════════════════════════════════════════════════════════════════════

    def chunk_document(self, content: str) -> list[str]:
        """
        Step 2: Split document into overlapping chunks.
        Chunks are semantic (by sentence) when possible.

        Returns:
            List of text chunks
        """
        # Split by paragraphs first
        paragraphs = content.split("\n\n")

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # If paragraph alone is larger than chunk_size, split it by sentences
            if len(paragraph) > self.chunk_size:
                sentences = self._split_sentences(paragraph)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                        chunks.append(current_chunk.strip())
                        # Add overlap
                        current_chunk = current_chunk[-self.chunk_overlap:] + sentence
                    else:
                        current_chunk += " " + sentence

            else:
                # Add paragraph to current chunk
                if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = current_chunk[-self.chunk_overlap:] + paragraph
                else:
                    current_chunk += "\n\n" + paragraph

        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]

    # ════════════════════════════════════════════════════════════════════════
    # Step 3 & 4: Integration (delegated to Ollama + VectorDB)
    # ════════════════════════════════════════════════════════════════════════

    async def enrich_rag(
        self,
        document_id: int,
        chunks: list[str],
        ollama_client,
        vector_db,
        embedding_model: str = "nomic-embed-text",
    ) -> dict:
        """
        Step 3 & 4: Generate embeddings and store in vector DB.

        Args:
            document_id: Document ID from vector DB
            chunks: List of text chunks
            ollama_client: Ollama client for embedding generation
            vector_db: Vector DB connection
            embedding_model: Model to use for embeddings

        Returns:
            Statistics about the enrichment process
        """
        stats = {
            "total_chunks": len(chunks),
            "embeddings_stored": 0,
            "errors": 0,
        }

        for i, chunk in enumerate(chunks):
            try:
                # Step 3: Generate embedding
                embedding = await ollama_client.generate_embedding(
                    text=chunk,
                    model=embedding_model,
                )

                if embedding:
                    # Step 4: Store embedding in vector DB
                    await vector_db.store_embedding(
                        document_id=document_id,
                        chunk_text=chunk,
                        embedding=embedding,
                    )
                    stats["embeddings_stored"] += 1
                else:
                    stats["errors"] += 1

            except Exception as e:
                print(f"Error processing chunk {i}: {e}")
                stats["errors"] += 1

        # Mark document as processed
        await vector_db.mark_processed(document_id)

        return stats

    # ════════════════════════════════════════════════════════════════════════
    # Full Pipeline
    # ════════════════════════════════════════════════════════════════════════

    async def process_document_full_pipeline(
        self,
        file_path: str,
        vector_db,
        ollama_client,
        embedding_model: str = "nomic-embed-text",
    ) -> dict:
        """
        Execute full 4-step RAG pipeline:
        1. Load document
        2. Chunk document
        3. Generate embeddings
        4. Store in vector DB

        Returns:
            Pipeline execution results
        """
        print(f"[Pipeline] Step 1: Loading document from {file_path}")
        content, metadata = await self.load_document(file_path)

        print(f"[Pipeline] Step 2: Chunking document (chunk_size={self.chunk_size})")
        chunks = self.chunk_document(content)

        print(f"[Pipeline] Step 3 & 4: Generating embeddings and storing ({len(chunks)} chunks)")
        document_id = await vector_db.store_document(
            filename=metadata["filename"],
            content=content,
            metadata=metadata,
            content_hash=metadata["content_hash"],
        )

        enrichment_stats = await self.enrich_rag(
            document_id=document_id,
            chunks=chunks,
            ollama_client=ollama_client,
            vector_db=vector_db,
            embedding_model=embedding_model,
        )

        return {
            "document_id": document_id,
            "filename": metadata["filename"],
            "content_length": len(content),
            "chunks": len(chunks),
            "enrichment_stats": enrichment_stats,
            "metadata": metadata,
        }
