from datasets import load_dataset
from langchain_core.documents import Document
from ingest_pipeline import clean_docs, chunk_docs
from vector_store import store_documents

dataset = load_dataset("pacovaldez/stackoverflow-questions", split="train", streaming=True)

sample = []
for row in dataset:
    text = row["title"] + "\n\n" + row["body"]
    sample.append(Document(page_content=text, metadata={"label": row["label"]}))
    if len(sample) >= 500:
        break

clean = clean_docs(sample)
chunks = chunk_docs(clean)
store_documents(chunks)
print(f"loaded {len(sample)} stackoverflow questions, stored {len(chunks)} chunks")
