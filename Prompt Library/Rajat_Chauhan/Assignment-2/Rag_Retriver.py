from  embeddings import rag_retriever

from langchain_openai import OpenAI

from  llm_coforge import llm

#llm = OpenAI(model="gpt-5-2-chat", temperature=0.7, openai_api_key=openaiapi_key)


## Simple Rag function to demonstrate retrieval and generation
# def rag_generate(query: str, rag_retriever,llm,top_k: int) -> str:
#     print(f"\n**** RAG Generation for query: '{query}'")
#     try:
#         # Step 1: Retrieve relevant documents
#         retrieval_results = rag_retriever.retrieve(query, top_k=top_k, score_threshold=0.5)
        
#         # Extract retrieved documents
#         retrieved_docs = retrieval_results['documents'][0] if retrieval_results['documents'] else []
#         print(f"✓ Retrieved {len(retrieved_docs)} documents for generation.")
        
#         # Step 2: Generate response using LLM with retrieved documents as context
#         if not retrieved_docs:
#             print("⚠️ No relevant documents retrieved. Generating response without context.")
#             response = ""
#             return response
#         else:
#             context = "\n\n".join(retrieved_docs)  # Combine retrieved documents into context
#             prompt = f"Based on the following retrieved information:\n{context}\n\nAnswer the question: {query}"
#             response = llm.invoke(prompt.format(context=context, query=query))
#             print(f"✓ Generated response: {response}")
#             return response.content

#     except Exception as e:
#         print(f"✗ Error during RAG generation: {e}")
#         raise


def rag_generate_coforge_leaves(query: str, rag_retriever,llm,top_k: int) -> list:
    print(f"\n**** RAG Generation for query: '{query}'")

    try:
        # Step 1: Retrieve relevant documents
        retrieval_results = rag_retriever.retrieve(query, top_k=top_k, score_threshold=0.5)
        
        # Extract retrieved documents
        retrieved_docs = retrieval_results['documents'][0] if retrieval_results['documents'] else []
        print(f"✓ Retrieved {len(retrieved_docs)} documents for generation.")
        
        # Step 2: Generate response using LLM with retrieved documents as context
        if not retrieved_docs:
            print("⚠️ No relevant documents retrieved. Generating response without context.")
            response = ""
            return response
        else:
            context = "\n\n".join(retrieved_docs)  # Combine retrieved documents into context
            prompt = f"Based on the following retrieved information:\n{context}\n\nAnswer the question: {query}"
            response = llm.invoke(prompt.format(context=context, query=query))
            print(f"✓ Generated response: {response}")
            return response

    except Exception as e:
        print(f"✗ Error during RAG generation: {e}")
        raise

print(rag_generate_coforge_leaves("how many types of leaves are there in coforge", rag_retriever,llm, top_k=3))