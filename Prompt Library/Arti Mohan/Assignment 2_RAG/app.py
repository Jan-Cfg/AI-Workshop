from pathlib import Path

DOCS_DIR = Path("docs")


def load_documents():
    documents = []
    for file_path in DOCS_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8").strip()
        documents.append({"name": file_path.name, "text": text})
    return documents


def simple_retrieve(question, documents, top_k=2):
    question_words = set(question.lower().split())
    scored_documents = []

    for document in documents:
        document_words = set(document["text"].lower().split())
        score = len(question_words.intersection(document_words))
        scored_documents.append((score, document))

    scored_documents.sort(key=lambda item: item[0], reverse=True)
    return [document for score, document in scored_documents[:top_k] if score > 0]


def plain_answer(question):
    return (
        "Clean code usually means using readable names, small functions, "
        "and good exception handling. This is a generic answer without local context."
    )


def rag_answer(question, retrieved_documents):
    if not retrieved_documents:
        return "No relevant documents were found for the question."

    context = "\n\n".join(
        [f"[{document['name']}]\n{document['text']}" for document in retrieved_documents]
    )

    return (
        "This is a RAG-style grounded answer based on retrieved documents:\n\n"
        f"{context}\n\n"
        f"Question: {question}\n\n"
        "Summary Answer: This project should follow clean code practices such as using "
        "clear names, keeping functions focused on one responsibility, splitting long "
        "functions into smaller helpers, avoiding unnecessary nesting, and handling "
        "exceptions with specific error handling and useful logs."
    )


def main():
    documents = load_documents()
    question = "What clean code practices should be followed in this Python project?"

    print("\n=== QUESTION ===")
    print(question)

    print("\n=== DOCUMENTS LOADED ===")
    for document in documents:
        print(f"- {document['name']}")

    print("\n=== WITHOUT RAG ===")
    print(plain_answer(question))

    retrieved_documents = simple_retrieve(question, documents)

    print("\n=== RETRIEVED DOCUMENTS ===")
    if retrieved_documents:
        for document in retrieved_documents:
            print(f"- {document['name']}")
    else:
        print("No relevant documents found.")

    print("\n=== WITH RAG ===")
    print(rag_answer(question, retrieved_documents))


if __name__ == "__main__":
    main()
