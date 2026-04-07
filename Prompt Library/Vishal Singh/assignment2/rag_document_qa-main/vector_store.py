from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector


def get_vector_store():
    db_connection = "postgresql+psycopg://postgres:postgres@localhost:5432/rag_db" 
    collection_name = "enterprise_ai"
    embeddings=OllamaEmbeddings(model="mxbai-embed-large")
    db=PGVector(embeddings=embeddings,
             collection_name=collection_name,
             connection=db_connection)
    return db