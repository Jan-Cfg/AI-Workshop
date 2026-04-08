from fastapi import FastAPI, HTTPException
import requests
import chromadb
from chromadb.config import Settings

# -----------------------------
# FastAPI init
# -----------------------------
app = FastAPI()

# -----------------------------
# ChromaDB (Disk-persistent)
# -----------------------------
client = chromadb.Client(
    Settings(
        persist_directory="./chroma_store"
    )
)

collection = client.get_or_create_collection("documents")

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
def root():
    return {"status": "API is running"}

# -----------------------------
# Chat endpoint (basic LLM)
# -----------------------------
@app.post("/chat")
def chat(req: dict):
    payload = {
        "model": "mistral",
        "prompt": req["prompt"],
        "stream": False,
        "options": {
            "num_predict": 200
        }
    }

    r = requests.post(
        "http://localhost:11434/api/generate",
        json=payload
    )

    result = r.json()

    if "response" not in result:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Ollama did not return expected response",
                "ollama_output": result
            }
        )

    return {"response": result["response"]}

# -----------------------------
# Embedding helper
# -----------------------------
def embed_text(text: str):
    r = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "mistral",
            "prompt": text
        }
    )
    return r.json()["embedding"]

# -----------------------------
# Document ingestion (RAG step 1-4)
# -----------------------------
def ingest_document(text: str):
    chunks = [text[i:i+300] for i in range(0, len(text), 300)]

    for idx, chunk in enumerate(chunks):
        collection.add(
            ids=[f"doc_{idx}"],
            documents=[chunk],
            embeddings=[embed_text(chunk)]
        )

# -----------------------------
# RAG query logic
# -----------------------------
def rag_query(question: str):
    q_embedding = embed_text(question)

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=3
    )

    context = " ".join(results["documents"][0])

    final_prompt = f"""
Context:
{context}

Question:
{question}

Answer:
"""

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": final_prompt,
            "stream": False,
            "options": {"num_predict": 200}
        }
    )

    return r.json()["response"]

# -----------------------------
# RAG API
# -----------------------------
@app.post("/rag")
def rag_api(req: dict):
    return {"response": rag_query(req["prompt"])}

# -----------------------------
# Initial demo ingestion
# -----------------------------
ingest_document(
    "Artificial Intelligence (AI) is a technology that enables computers to simulate human intelligence. It is widely used in fields such as education, healthcare, and finance."
)