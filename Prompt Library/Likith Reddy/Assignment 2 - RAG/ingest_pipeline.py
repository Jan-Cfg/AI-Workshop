import sys
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader, UnstructuredMarkdownLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vector_store import store_documents


def load_file(path):
    p = Path(path)
    loaders = {".pdf": PDFPlumberLoader, ".md": UnstructuredMarkdownLoader, ".csv": CSVLoader}
    loader = loaders.get(p.suffix, TextLoader)
    return loader(str(p)).load()


def clean_docs(docs):
    out = []
    for d in docs:
        text = " ".join(d.page_content.split())
        if len(text) > 100:
            d.page_content = text
            out.append(d)
    return out


def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    return splitter.split_documents(docs)


def run_pipeline(path):
    raw = load_file(path)
    clean = clean_docs(raw)
    chunks = chunk_docs(clean)
    store_documents(chunks)
    print(f"done - {len(chunks)} chunks stored from {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python ingest_pipeline.py <file>")
        sys.exit(1)
    run_pipeline(sys.argv[1])
