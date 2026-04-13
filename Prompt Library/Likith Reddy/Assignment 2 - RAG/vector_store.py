from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


def get_store():
    emb = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(collection_name="knowledge_base", embedding_function=emb, persist_directory="./chroma_store")


def store_documents(docs):
    get_store().add_documents(docs)


def retrieve(query, top_k=5):
    results = get_store().similarity_search(query, k=top_k)
    if not results:
        return ""
    return "\n\n".join(d.page_content for d in results)
