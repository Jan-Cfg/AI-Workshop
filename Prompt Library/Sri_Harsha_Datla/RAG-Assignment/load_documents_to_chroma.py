import glob
from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,
    PDFPlumberLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chroma_db import upload_to_chroma


def load_documents_from_folder(folder_path: str, file_patterns: list = None) -> list:
    """
    Load documents from a folder called documents. Thse documents will then be split into chunks and fed to the Vector DB in the subsequent steps.
    """
    if file_patterns is None:
        file_patterns = ['*.txt', '*.pdf', '*.md', '*.csv']
    
    documents = []
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        raise ValueError(f"Folder path does not exist: {folder_path}")
    
    print(f"Loading documents from: {folder_path}")
    
    for pattern in file_patterns:
        files = glob.glob(str(folder_path / pattern), recursive=False)
        
        for file_path in files:
            print(f"  Loading: {file_path}")
            try:
                if file_path.endswith('.pdf'):
                    loader = PDFPlumberLoader(file_path)
                elif file_path.endswith('.md'):
                    loader = UnstructuredMarkdownLoader(file_path)
                elif file_path.endswith('.csv'):
                    loader = CSVLoader(file_path)
                else:  # .txt and other text files
                    loader = TextLoader(file_path)
                
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded successfully ({len(docs)} pages/chunks)")
            
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


def split_documents(documents: list, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Split documents int chunks based on the specification in the arguments. WARNING: This process takes several hours for larger documents if you do not have a powerful GPU.
    chunk overlap chosen as 20% of the chunk size
    """
    print(f"\nSplitting documents (chunk_size={chunk_size}, overlap={chunk_overlap})...")

    # Method from Langchain used to split text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    split_docs = splitter.split_documents(documents)
    print(f"Total chunks created: {len(split_docs)}")
    
    return split_docs


def main():
    # Configuration
    FOLDER_PATH = "./documents"  # Change this to your documents folder
    FILE_PATTERNS = ['*.txt', '*.pdf', '*.md', '*.csv']
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    CHROMA_PERSIST_DIR = "./chroma_db"
    EMBEDDING_MODEL = "nomic-embed-text"  # Change to your preferred embedding model
    COLLECTION_NAME = "documents"
    
    try:
        # Step 1: Load documents from folder
        documents = load_documents_from_folder(FOLDER_PATH, FILE_PATTERNS)
        
        if not documents:
            print("No documents found. Exiting.")
            return
        
        # Step 2: Split documents into chunks
        split_docs = split_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
        
        # Step 3: Upload to Chroma DB
        vector_store = upload_to_chroma(
            split_docs,
            persist_directory=CHROMA_PERSIST_DIR,
            model_name=EMBEDDING_MODEL,
            collection_name=COLLECTION_NAME
        )
        
        print("Document loading completed successfully!")
        print(f"Documents processed: {len(documents)}")
        print(f"Chunks created: {len(split_docs)}")
        print(f"Chroma DB location: {CHROMA_PERSIST_DIR}")
        
    except Exception as e:
        print(f"\nError during processing: {e}")
        raise


if __name__ == "__main__":
    main()

