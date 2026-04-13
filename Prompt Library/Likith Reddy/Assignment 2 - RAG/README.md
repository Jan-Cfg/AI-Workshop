# Assignment 2 - RAG

using llama3.2 via ollama, chromadb for vector store, and the stackoverflow questions dataset from huggingface

## setup

pull the models first

```
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

then install deps

```
pip install -r requirements.txt
```

## how to run

load the stackoverflow dataset into chromadb (streams 500 questions, takes a minute)

```
python load_hf_dataset.py
```

then start the chat

```
python rag_chat.py
```

type `demo` to see structured output, `quit` to exit

to ingest your own file

```
python ingest_pipeline.py <your_file>
```

## files

- `rag_chat.py` - main chat, has system prompt / user prompt / tools / ai messages / structured output
- `vector_store.py` - chromadb wrapper
- `ingest_pipeline.py` - load -> clean -> chunk -> embed+store
- `load_hf_dataset.py` - pulls stackoverflow questions from huggingface into the vector store
- `security_ai.md` - notes on securing ai products (input / data / output)
