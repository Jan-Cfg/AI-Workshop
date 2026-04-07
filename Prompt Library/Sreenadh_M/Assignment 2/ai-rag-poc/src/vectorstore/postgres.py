"""
PostgreSQL Vector Database with pgvector Extension
Manages document embeddings and similarity search for RAG.
"""
import json
from typing import Optional, Any
import psycopg
from psycopg.rows import dict_row


class PostgresVectorStore:
    """PostgreSQL with pgvector extension for RAG."""

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ):
        self.connection_string = (
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )
        self.conn: Optional[psycopg.AsyncConnection] = None

    async def connect(self) -> None:
        """Establish database connection."""
        self.conn = await psycopg.AsyncConnection.connect(self.connection_string)
        await self._initialize_schema()

    async def close(self) -> None:
        """Close database connection."""
        if self.conn:
            await self.conn.aclose()

    async def _initialize_schema(self) -> None:
        """Initialize vector DB schema with pgvector extension."""
        async with self.conn.cursor() as cur:
            # Create pgvector extension
            await cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # Create documents table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    content_hash VARCHAR(64),
                    chunk_index INT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                );
            """)

            # Create document embeddings table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id SERIAL PRIMARY KEY,
                    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_text TEXT NOT NULL,
                    embedding vector(384),
                    similarity_score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT document_embeddings_unique UNIQUE(document_id, chunk_text)
                );
            """)

            # Create index on embeddings
            await cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON document_embeddings 
                USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
            """)

            # Create analysis results table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id SERIAL PRIMARY KEY,
                    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
                    analysis_type VARCHAR(100),
                    result JSONB,
                    confidence FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            await self.conn.commit()

    # ════════════════════════════════════════════════════════════════════════
    # Document Management
    # ════════════════════════════════════════════════════════════════════════

    async def store_document(
        self,
        filename: str,
        content: str,
        metadata: dict | None = None,
        content_hash: str = "",
    ) -> int:
        """Store document and return its ID."""
        async with self.conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO documents (filename, content, content_hash, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (filename, content, content_hash, json.dumps(metadata or {})))

            doc_id = (await cur.fetchone())[0]
            await self.conn.commit()
            return doc_id

    async def get_document(self, doc_id: int) -> dict | None:
        """Retrieve document by ID."""
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM documents WHERE id = %s;",
                (doc_id,)
            )
            return await cur.fetchone()

    async def list_documents(self, processed_only: bool = False) -> list[dict]:
        """List all documents."""
        async with self.conn.cursor(row_factory=dict_row) as cur:
            if processed_only:
                await cur.execute("SELECT * FROM documents WHERE processed = TRUE;")
            else:
                await cur.execute("SELECT * FROM documents;")
            return await cur.fetchall()

    # ════════════════════════════════════════════════════════════════════════
    # Embedding Management
    # ════════════════════════════════════════════════════════════════════════

    async def store_embedding(
        self,
        document_id: int,
        chunk_text: str,
        embedding: list[float],
    ) -> int:
        """Store document chunk with its embedding."""
        async with self.conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO document_embeddings (document_id, chunk_text, embedding)
                VALUES (%s, %s, %s::vector)
                ON CONFLICT (document_id, chunk_text) 
                DO UPDATE SET embedding = EXCLUDED.embedding
                RETURNING id;
            """, (document_id, chunk_text, json.dumps(embedding)))

            embedding_id = (await cur.fetchone())[0]
            await self.conn.commit()
            return embedding_id

    async def similarity_search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        threshold: float = 0.7,
    ) -> list[dict]:
        """Find similar documents using cosine similarity."""
        async with self.conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                SELECT 
                    de.id,
                    de.document_id,
                    d.filename,
                    de.chunk_text,
                    1 - (de.embedding <=> %s::vector) as similarity
                FROM document_embeddings de
                JOIN documents d ON de.document_id = d.id
                WHERE 1 - (de.embedding <=> %s::vector) > %s
                ORDER BY similarity DESC
                LIMIT %s;
            """, (json.dumps(query_embedding), json.dumps(query_embedding), threshold, limit))

            return await cur.fetchall()

    # ════════════════════════════════════════════════════════════════════════
    # Analysis Results
    # ════════════════════════════════════════════════════════════════════════

    async def store_analysis(
        self,
        document_id: int,
        analysis_type: str,
        result: dict,
        confidence: float = 1.0,
    ) -> int:
        """Store analysis results for a document."""
        async with self.conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO analysis_results (document_id, analysis_type, result, confidence)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (document_id, analysis_type, json.dumps(result), confidence))

            analysis_id = (await cur.fetchone())[0]
            await self.conn.commit()
            return analysis_id

    # ════════════════════════════════════════════════════════════════════════
    # Status Updates
    # ════════════════════════════════════════════════════════════════════════

    async def mark_processed(self, document_id: int) -> None:
        """Mark document as processed (RAG enriched)."""
        async with self.conn.cursor() as cur:
            await cur.execute("""
                UPDATE documents 
                SET processed = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """, (document_id,))

            await self.conn.commit()

    async def delete_document(self, document_id: int) -> None:
        """Delete document and its embeddings."""
        async with self.conn.cursor() as cur:
            await cur.execute("DELETE FROM documents WHERE id = %s;", (document_id,))
            await self.conn.commit()
        self.connection.commit()

    def retrieve_vector(self, query_vector, limit=5):
        self.cursor.execute("""
            SELECT vector, metadata FROM vectors
            ORDER BY (vector <-> %s) LIMIT %s
        """, (query_vector, limit))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()