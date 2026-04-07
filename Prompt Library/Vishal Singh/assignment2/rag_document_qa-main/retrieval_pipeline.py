from vector_store import get_vector_store

def query_pgvector(query:str):
    db=get_vector_store()
    results=db.similarity_search_with_score(query,k=3)
    return results