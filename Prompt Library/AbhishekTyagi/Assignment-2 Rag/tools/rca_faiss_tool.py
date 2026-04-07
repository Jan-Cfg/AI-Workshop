from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from llms.coforgeTextEmbeddings import CustomEmbeddings

embeddings = CustomEmbeddings()

vectorstore = FAISS.load_local(
    "rca_faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

@tool
def rca_doc_search(query: str) -> str:
    """
    Search RCA knowledge base (FAISS) for fix steps,
    SQL, API calls, and folder paths.
    """
    docs = vectorstore.similarity_search(query, k=3)
    return "\n\n".join(d.page_content for d in docs)