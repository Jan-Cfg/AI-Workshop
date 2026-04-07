from langchain_community.document_loaders import TextLoader,DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from vector_store import get_vector_store
from retrieval_pipeline import query_pgvector
from langchain_ollama.llms import OllamaLLM
from langchain_core.messages import HumanMessage,SystemMessage
from ollama import chat
from langchain_ollama import ChatOllama
#import requests
#import json

def load_documents(docPath:str):
    """ Load documents from docpath"""
    if not os.path.exists(docPath):
        raise FileExistsError(f"No such {docPath} exists")
    
    loader=DirectoryLoader(path=docPath,glob="*.txt",loader_cls=TextLoader)
    documents=loader.load()
    if len(documents) == 0:
        raise FileExistsError(f"no file exists under directory {docPath}")
    
    return documents

def chunk_documents(documents:list,chunk_size:int = 300,chunk_Overlap:int = 70):
   if len(documents)==0:
       raise ValueError("No documents to split")
   textSplitter= RecursiveCharacterTextSplitter(chunk_size = chunk_size,chunk_overlap=chunk_Overlap)
   return textSplitter.split_documents(documents=documents)

def embed_documents(texts:list):
    db=get_vector_store()
    db.add_documents(texts)

#def main():
def run_ingestion(doc_path = "docs"):

    #1.Loading the file
    documents=load_documents(docPath="docs")
    print("Loaded documents:", len(documents))
    
    #2.Chunking the file
    texts=chunk_documents(documents,chunk_size=300,chunk_Overlap=70)
    print("Total chunks:", len(texts))

    #3.Embedding and storing in pgVector
    embed_documents(texts)
    print("Embeddings done succesfully")
    
    return len(texts)

