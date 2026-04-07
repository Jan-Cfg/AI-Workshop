# AI Retrieval-Augmented Generation POC

This is a POC that cannot be proven (sadly).
There are many blockers to get this working or getting tested. Coforge will not allow access to ollama.ai and will not allow to install Docker without administrator privileges. If you manage to bypass all these, you can see that:

It demonstrates:
- **Ollama integration** with context engineering (system prompts, tools, structured output)
- **PostgreSQL Vector DB** with pgvector for efficient similarity search
- **4-step document enrichment pipeline** (load → chunk → embed → store)
- **Comprehensive security** across infrastructure, data, and AI layers

## Project Structure

```
ai-rag-poc
├── src
│   ├── main.py                # Entry point with RAG orchestration
│   ├── config.py              # Configuration management
│   ├── ollama                 # Ollama model communication with context engineering
│   │   ├── __init__.py
│   │   └── client.py          # System prompts, tools, structured output
│   ├── rag                    # RAG pipeline components
│   │   ├── __init__.py
│   │   ├── retriever.py       # Vector similarity search
│   │   └── generator.py       # LLM response generation with context
│   ├── vectorstore            # Vector database interaction
│   │   ├── __init__.py
│   │   ├── postgres.py        # PostgreSQL + pgvector implementation
│   │   └── pinecone.py        # Optional: Pinecone vector DB
│   ├── security               # Security mechanisms
│   │   ├── __init__.py
│   │   ├── auth.py            # Token-based authentication
│   │   └── encryption.py      # Data encryption at rest
│   └── utils                  # Utility functions
│       ├── __init__.py
│       ├── helpers.py         # Input validation, sanitization, logging
│       └── document_processor.py  # 4-step RAG pipeline
├── tests                      # Comprehensive unit tests
│   ├── __init__.py
│   ├── test_ollama.py         # Context engineering tests
│   ├── test_rag.py            # RAG pipeline tests
│   └── test_security.py       # Authentication & encryption tests
├── docs
│   └── SECURITY.md            # Complete security documentation
├── requirements.txt           # Project dependencies
├── .env.example               # Example environment variables
├── README.md                  # This file
└── setup.py                   # Setup script
```

## Setup Instructions

### Quick Start with Docker (Recommended)

**Prerequisites:**
- Docker (https://docker.com)
- Docker Compose

**One-command setup:**
```bash
# Start all services (PostgreSQL, Ollama, RAG App)
docker-compose up -d

# Initialize Ollama models (bash on macOS/Linux)
bash ./init-ollama.sh

# Or on Windows PowerShell
.\init-ollama.bat

# View logs
docker-compose logs -f rag-app

# Stop services
docker-compose down
```

The application will be ready at `http://localhost:8000` after initialization!

---

### Manual Setup (Without Docker)

**Prerequisites:**
- Python 3.9+
- PostgreSQL 13+ (with pgvector extension)
- Ollama (https://ollama.ai)

### Manual Setup Step 1: Install PostgreSQL pgvector Extension
```bash
# On Ubuntu/Debian
sudo apt-get install postgresql-contrib postgresql-server-dev-all
sudo -u postgres psql
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Manual Setup Step 2: Clone & Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Manual Setup Step 3: Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

Example `.env` content:
```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
EMBEDDING_MODEL=nomic-embed-text

# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_database
DB_USER=postgres
DB_PASSWORD=your_password

# RAG Configuration
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_SIMILARITY_THRESHOLD=0.7
RAG_TOP_K=5

# Security
API_KEY=your_secret_api_key
ENCRYPTION_KEY=your_encryption_key
```

### Manual Setup Step 4: Initialize Database
```bash
# Create database
createdb -U postgres rag_database

# Connect and enable pgvector
psql -U postgres -d rag_database
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Manual Setup Step 5: Start Ollama
```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull mistral
ollama pull nomic-embed-text  # For embeddings
```

## Usage Examples

### Basic RAG Query

```python
import asyncio
from src.main import RAGApplication

async def example():
    app = RAGApplication()
    await app.initialize()
    
    # Query the RAG system
    response = await app.query_rag("What is machine learning?")
    
    await app.cleanup()

asyncio.run(example())
```

### Document Ingestion (4-step Pipeline)

```python
# The 4-step pipeline is automatic:
# 1. Load document from file
# 2. Chunk into semantic segments (500 tokens, 50 overlap)
# 3. Generate embeddings via Ollama
# 4. Store embeddings in PostgreSQL vector DB

result = await app.ingest_document("path/to/document.txt")

# Result includes:
# - document_id: ID in vector DB
# - chunks: Number of text chunks created
# - embeddings_stored: Successfully embedded chunks
# - enrichment_stats: Processing statistics
```

### Context Engineering Example

```python
from src.ollama.client import OllamaClient, ToolDefinition

client = OllamaClient(base_url="http://localhost:11434", model="mistral")

# System Prompt (defines AI behavior)
system_prompt = """You are a document analyst.
- Be concise and accurate
- Only use provided documents
- Cite sources"""

# Tool definitions (structured capabilities)
tools = [
    ToolDefinition(
        name="summarize",
        description="Create a summary of the document",
        parameters={"length": "short|medium|long"}
    ),
    ToolDefinition(
        name="extract_entities",
        description="Extract key entities",
        parameters={"types": "person|organization|concept"}
    )
]

# Generate response with full context
response = await client.generate_with_context(
    user_prompt="What are the main topics?",
    system_prompt=system_prompt,
    tools=tools,
    temperature=0.5  # Controlled randomness
)
```

### Structured Output (for AI Product Integration)

```python
# Get JSON-formatted analysis
analysis = await client.analyze_with_structured_output(
    content=document_content,
    analysis_task="Analyze sentiment and key insights"
)

# Returns:
# {
#     "summary": "...",
#     "key_insights": ["insight1", "insight2"],
#     "sentiment": "positive|neutral|negative",
#     "confidence": 0.85
# }
```

## Security Features

### 1. Infrastructure & Access Security
- **Tokenized authentication** with scope-based access control
- **Token expiration** (24 hours by default)
- **Rate limiting** (configurable requests/minute)
- **PostgreSQL row-level security** for data isolation

### 2. Data Security
- **Encryption at rest** using Fernet symmetric encryption
- **Encryption in transit** (HTTPS/TLS 1.3)
- **Input validation** to prevent SQL injection, XSS
- **Sensitive data masking** in logs

### 3. AI/Model Security
- **Prompt injection prevention** via structured system prompts
- **Temperature control** (0.1-0.3 for safety-critical tasks)
- **RAG poisoning detection** via document validation
- **Audit logging** of all AI interactions
- **Output validation** for structured responses

**See [docs/SECURITY.md](docs/SECURITY.md) for comprehensive security documentation.**

## Testing

### Run All Tests
```bash
pytest tests/ -v --cov=src
```

### Run Specific Test Suites
```bash
# Test Ollama client (context engineering)
pytest tests/test_ollama.py -v

# Test RAG pipeline (retriever + generator)
pytest tests/test_rag.py -v

# Test security components (auth + encryption)
pytest tests/test_security.py -v
```

### Test Coverage
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   User Application                   │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────────┐     ┌──────▼──────┐
    │   Document   │     │   RAG Query  │
    │  Ingestion   │     │  Interface   │
    └────┬─────────┘     └──────┬───────┘
         │                      │
         │  4-Step Pipeline     │  Retrieval
         │  1. Load             │  + Generation
         ▼  2. Chunk            ▼
    ┌──────────────────────────────────────┐
    │     Ollama (LLM Service)             │
    │  - System Prompts                    │
    │  - User Prompts                      │
    │  - Tools & Functions                 │
    │  - Embeddings Generation             │
    │  - Structured Output                 │
    └────────┬─────────────────────────────┘
             │
             │ 3. Embeddings
             │ 4. Store
             ▼
    ┌──────────────────────────────────────┐
    │  PostgreSQL + pgvector               │
    │  - Document Storage                  │
    │  - Vector Embeddings                 │
    │  - Similarity Search (cosine)        │
    │  - Analysis Results                  │
    └──────────────────────────────────────┘
         │
         │  Security Layer
         │  - Encryption at rest
         │  - Row-level security
         │  - Audit logging
         ▼
    ┌──────────────────────────────────────┐
    │   Token Auth + Encryption            │
    │   Data Protection                    │
    │   Access Control                     │
    └──────────────────────────────────────┘
```

## Performance Optimization

### Vector Search Performance
```sql
-- Create IVFFlat index for faster similarity search
CREATE INDEX idx_embeddings_vector ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Query performance: ~50ms for 100K vectors
```

### Chunking Strategy
- **Chunk size**: 500 tokens (adjustable)
- **Overlap**: 50 tokens (prevents losing context between chunks)
- **Semantic chunking**: Splits on sentence boundaries when possible

### Connection Pooling
```python
# Production: Use connection pooling
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_POOL_PRE_PING = True
```

## Docker Deployment

### docker-compose Configuration

The project includes complete Docker Compose setup for all services:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg15-latest
    environment:
      POSTGRES_DB: rag_database
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      
  rag-app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_healthy
    environment:
      OLLAMA_BASE_URL: http://ollama:11434
      DB_HOST: postgres
      DB_PORT: 5432
```

**Key Features:**
- **Auto-initialization**: pgvector extension installed automatically
- **Health checks**: Services verify readiness before starting dependent services
- **Volume persistence**: PostgreSQL data and Ollama models persist across restarts
- **Service networking**: All services communicate via internal Docker network

### Quick Start
```bash
# Start all services
docker-compose up -d

# Initialize Ollama models (Linux/macOS)
bash ./init-ollama.sh

# Or Windows
.\init-ollama.bat

# Check status
docker-compose ps

# View logs
docker-compose logs -f rag-app

# Stop all services
docker-compose down

# Clean up (remove volumes and data)
docker-compose down -v
```

### Building Custom Images
```bash
# Build just the RAG app image
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Build specific service
docker-compose build rag-app
```

### Accessing Services Inside Docker
```bash
# Connect to PostgreSQL inside container
docker exec -it <postgres_id> psql -U postgres -d rag_database

# Connect to Ollama
docker exec -it <ollama_id> ollama list

# Check RAG app logs
docker-compose logs rag-app

# Shell into RAG app container
docker exec -it <rag_app_id> /bin/bash
```

### Volume Management
```bash
# Check volumes
docker volume ls | grep rag

# Inspect volume
docker volume inspect rag_postgres_data

# Remove all project volumes
docker-compose down -v
```

### Cloud Deployment
- **AWS**: ECS + RDS (PostgreSQL) + EC2
- **GCP**: Cloud Run + Cloud SQL + Compute Engine
- **Azure**: App Service + Database for PostgreSQL + Container Instances
- **Kubernetes**: Use docker-compose.yml as basis for k8s manifests

## Troubleshooting

### Ollama Not Responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Database Connection Error
```bash
# Check PostgreSQL connection
psql -U postgres -d rag_database -c "SELECT version();"

# Check pgvector extension
psql -U postgres -d rag_database -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Embedding Generation Slow
- Reduce `RAG_CHUNK_SIZE` to process smaller chunks
- Use smaller embedding model (e.g., `all-minilm` instead of `nomic-embed-text`)
- Enable batch processing for multiple documents

## Docker Troubleshooting

### Services Won't Start
```bash
# Check Docker daemon
docker ps

# View detailed logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d

# Check service status
docker-compose ps
```

### PostgreSQL Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Connect and verify pgvector
docker-compose exec postgres psql -U postgres -d rag_database -c "SELECT * FROM pg_extension;"

# Reset database (warning: deletes data)
docker-compose down -v
docker-compose up -d
```

### Ollama Models Not Loading
```bash
# Check Ollama logs
docker-compose logs ollama

# List available models
docker-compose exec ollama ollama list

# Manually pull models (inside container)
docker-compose exec ollama ollama pull mistral
docker-compose exec ollama ollama pull nomic-embed-text

# Check if models are loaded
curl http://localhost:11434/api/tags
```

### RAG App Connection Errors
```bash
# Check if app can reach Ollama
docker-compose exec rag-app curl http://ollama:11434/api/tags

# Check if app can reach PostgreSQL
docker-compose exec rag-app psql -h postgres -U postgres -d rag_database -c "SELECT 1"

# View app logs with timestamps
docker-compose logs --timestamps rag-app
```

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different ports in docker-compose.yml
# Change "8000:8000" to "8001:8000" to use port 8001
```

### Out of Memory
```bash
# Increase Docker memory allocation
# Edit Docker Desktop Settings → Resources → Memory: 8GB (recommended)

# Or limit memory in docker-compose.yml
services:
  rag-app:
    deploy:
      resources:
        limits:
          memory: 4G
```

### Volume Permission Issues
```bash
# Fix volume ownership (Linux only)
sudo chown -R 999:999 postgres_volume/

# Or run container with specific user
# Add to docker-compose.yml:
# postgres:
#   user: "999:999"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Security Reporting

For security vulnerabilities, please email security@example.com instead of using the issue tracker.

## Support

For support and questions:
- Documentation: See [docs/SECURITY.md](docs/SECURITY.md)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## Changelog

### v1.0.0 (2024-04-07)
- Initial release
- Ollama client with context engineering
- PostgreSQL vector DB integration
- 4-step RAG pipeline
- Comprehensive security features
- Full test coverage
- Security documentation
