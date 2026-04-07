from ingestion_pipeline import run_ingestion
from retrieval_pipeline import query_pgvector
from llm_service import generate_answer


def main():
    chunks=run_ingestion("docs")
    print(f"ingested chunks:{chunks}")
    query = "What is Artificial Intelligence in enterprises?"
    results = query_pgvector(query)
    data=generate_answer(query,results)
    print(data["message"]["content"])

if __name__ == "__main__":
    main()    

