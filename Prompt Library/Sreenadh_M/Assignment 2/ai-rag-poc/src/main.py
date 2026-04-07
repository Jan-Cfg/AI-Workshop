"""
Main Entry Point for AI RAG Application
Demonstrates complete RAG pipeline with Ollama, Vector DB, and context engineering.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from ollama.client import OllamaClient, ToolDefinition
from vectorstore.postgres import PostgresVectorStore
from rag.retriever import Retriever
from rag.generator import Generator
from utils.document_processor import DocumentProcessor
from utils.helpers import validate_query, log_message
from security.auth import Auth
from security.encryption import EncryptionManager


class RAGApplication:
    """Main RAG Application orchestrator."""

    def __init__(self, config_env: str = "development"):
        self.config = get_config(config_env)
        self.config.validate()

        self.ollama_client = None
        self.vector_db = None
        self.retriever = None
        self.generator = None
        self.doc_processor = None
        self.auth = None

    async def initialize(self) -> None:
        """Initialize all components."""
        print("\n🚀 Initializing RAG Application...\n")

        # Initialize Ollama client
        self.ollama_client = OllamaClient(
            base_url=self.config.OLLAMA_BASE_URL,
            model=self.config.OLLAMA_MODEL,
        )

        # Check Ollama connectivity
        if not await self.ollama_client.check_health():
            raise ConnectionError(f"Ollama not responding at {self.config.OLLAMA_BASE_URL}")
        print(f"✓ Ollama connected ({self.config.OLLAMA_MODEL})")

        # Initialize Vector DB
        self.vector_db = PostgresVectorStore(
            host=self.config.DB_HOST,
            port=self.config.DB_PORT,
            database=self.config.DB_NAME,
            user=self.config.DB_USER,
            password=self.config.DB_PASSWORD,
        )

        await self.vector_db.connect()
        print(f"✓ Vector DB connected ({self.config.DB_NAME})")

        # Initialize RAG components
        self.retriever = Retriever(
            vector_db=self.vector_db,
            embedding_client=self.ollama_client,
            top_k=self.config.RAG_TOP_K,
            threshold=self.config.RAG_SIMILARITY_THRESHOLD,
        )

        self.generator = Generator(
            ollama_client=self.ollama_client,
            system_prompt="""You are a helpful AI assistant powered by RAG (Retrieval-Augmented Generation).
You answer questions based on your knowledge base. Always cite your sources.
If information is not available, say so explicitly."""
        )

        self.doc_processor = DocumentProcessor(
            chunk_size=self.config.RAG_CHUNK_SIZE,
            chunk_overlap=self.config.RAG_CHUNK_OVERLAP,
        )

        # Initialize security
        self.auth = Auth(secret_key=self.config.API_KEY)

        print("✓ RAG pipeline ready\n")

    async def ingest_document(self, file_path: str) -> dict:
        """
        Ingest a document with 4-step RAG pipeline.

        Args:
            file_path: Path to document

        Returns:
            Ingestion result
        """
        try:
            print(f"\n📄 Ingesting document: {file_path}")

            result = await self.doc_processor.process_document_full_pipeline(
                file_path=file_path,
                vector_db=self.vector_db,
                ollama_client=self.ollama_client,
                embedding_model=self.config.EMBEDDING_MODEL,
            )

            print(f"✓ Document ingested successfully")
            print(f"  - Document ID: {result['document_id']}")
            print(f"  - Chunks: {result['chunks']}")
            print(f"  - Embeddings stored: {result['enrichment_stats']['embeddings_stored']}\n")

            return result

        except Exception as e:
            print(f"✗ Error ingesting document:  {e}\n")
            return {"error": str(e)}

    async def query_rag(self, query: str) -> str:
        """
        Query the RAG system.

        Args:
            query: User query

        Returns:
            Generated response
        """
        try:
            validate_query(query)

            print(f"\n🔍 Query: {query}")

            # Retrieve relevant documents
            retrieved_docs = await self.retriever.retrieve(query)

            if not retrieved_docs:
                print("⚠ No relevant documents found in knowledge base")
                return "I don't have relevant information about this query."

            print(f"📚 Retrieved {len(retrieved_docs)} relevant document(s)")

            # Generate response
            response = await self.generator.generate_response(
                query=query,
                context_documents=retrieved_docs,
                temperature=0.5,
            )

            print(f"\n📝 Response: {response}\n")

            return response

        except ValueError as e:
            print(f"✗ Invalid query: {e}\n")
            return ""
        except Exception as e:
            print(f"✗ Error processing query: {e}\n")
            return ""

    async def analyze_document_content(self, content: str) -> dict:
        """
        Analyze document content with context engineering.

        Demonstrates:
        - System prompt (role)
        - User prompt (task)
        - Structured output

        Args:
            content: Document content

        Returns:
            Analysis result with key insights
        """
        system_prompt = """You are an expert document analyst specializing in:
- Key insight extraction
- Content summarization
- Pattern identification

Respond as JSON."""

        analysis_task = "Analyze the following document and extract key insights:"

        result = await self.ollama_client.analyze_with_structured_output(
            content=content,
            analysis_task=analysis_task,
            system_prompt=system_prompt,
        )

        return result

    async def list_knowledge_base(self) -> None:
        """List all documents in knowledge base."""
        documents = await self.vector_db.list_documents(processed_only=True)

        if not documents:
            print("\n📚 Knowledge base is empty\n")
            return

        print(f"\n📚 Knowledge Base ({len(documents)} documents):\n")
        for doc in documents:
            print(f"  [{doc['id']}] {doc['filename']}")
            print(f"      Size: {len(doc['content'])} bytes")
            print(f"      Processed: {doc['processed']}\n")

    async def cleanup(self) -> None:
        """Clean up resources."""
        print("\n🛑 Shutting down...\n")
        if self.ollama_client:
            await self.ollama_client.close()
        if self.vector_db:
            await self.vector_db.close()


async def main():
    """Main application flow."""
    app = RAGApplication(config_env="development")

    try:
        await app.initialize()

        # Example: Ingest a document
        # await app.ingest_document("path/to/document.txt")

        # Example: Query RAG
        response = await app.query_rag("What is this system about?")

        # List knowledge base
        await app.list_knowledge_base()

    except Exception as e:
        print(f"✗ Application error: {e}")
        sys.exit(1)

    finally:
        await app.cleanup()


if __name__ == "__main__":
    asyncio.run(main())