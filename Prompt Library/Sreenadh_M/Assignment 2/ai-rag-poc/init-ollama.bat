@echo off
REM Script to initialize Ollama models on Windows
REM Run this after docker-compose is up

echo Waiting for Ollama to be ready...
timeout /t 10

echo Pulling Ollama models...
docker exec rag_ollama ollama pull mistral
docker exec rag_ollama ollama pull nomic-embed-text

echo Models loaded successfully!
docker exec rag_ollama ollama list
