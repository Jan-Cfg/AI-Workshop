from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from tqdm import tqdm


def upload_to_chroma(
        documents: list,
        persist_directory: str = "./chroma_db",
        model_name: str = "nomic-embed-text",
        collection_name: str = "documents"
) -> Chroma:
    """
    Upload documents to Chroma DB.
    """
    print(f"\nInitializing embeddings with model: {model_name}...")
    embeddings = OllamaEmbeddings(model=model_name)

    print(f"Uploading documents to Chroma DB...")
    print(f"  Collection: {collection_name}")
    print(f"  Persist directory: {persist_directory}")

    # Initialize Chroma vector store without documents
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    # Add documents with progress bar
    with tqdm(total=len(documents), desc="Adding chunks to Chroma DB") as pbar:
        for doc in documents:
            vector_store.add_documents([doc])
            pbar.update(1)

    print("Successfully uploaded documents to Chroma DB")
    return vector_store


def retrieve_context_from_chroma(query: str, chroma_dir: str = "./chroma_db", k: int = 10) -> str:
    """
    Retrieve relevant documents from Chroma DB based on the query.
    """
    try:
        # Initialize embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")

        # Load the Chroma vector store
        vector_store = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embeddings,
            collection_name="documents"
        )

        # Retrieve relevant documents
        retrieved_docs = vector_store.similarity_search(query, k=k)

        if not retrieved_docs:
            return ""

        # Format the context from retrieved documents
        context = "\n\n".join([f"[Source {i + 1}]\n{doc.page_content}"
                               for i, doc in enumerate(retrieved_docs)])
        return context

    except Exception as e:
        print(f"Warning: Could not retrieve context from Chroma DB: {e}")
        return ""