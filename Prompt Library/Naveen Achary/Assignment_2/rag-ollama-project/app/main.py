from fastapi import FastAPI
import requests

from rag import retrieve
from pipeline import enrich_rag
from config import OLLAMA_URL, MODEL_NAME

app = FastAPI()

SYSTEM_PROMPT = """You are a text analysis assistant.
Return JSON with:
- sentiment
- topic
- summary
"""

def call_ollama(prompt: str):
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]

def build_prompt(user_input, context):
    return f"""
SYSTEM:
{SYSTEM_PROMPT}

CONTEXT:
{context}

USER:
{user_input}

Return valid JSON only.
"""

@app.post("/analyze")
def analyze(text: str):
    context = retrieve(text)
    prompt = build_prompt(text, context)
    result = call_ollama(prompt)

    return {"context": context, "response": result}

@app.post("/ingest")
def ingest(text: str):
    enrich_rag(text)
    return {"status": "Document added"}