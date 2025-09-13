# Combined RAG API

This folder contains a modular, server-deployable Retrieval Augmented Generation (RAG) system with a FastAPI interface. Each RAG technique is implemented as a separate module for easy extension and integration.


## Structure
- `main.py`: FastAPI server entry point
- `modules/`: Modular RAG components (retrieval, multi-query, fusion, decomposition, generation)
- `config.py`: **Single-point configuration** for all models and vector store
- `requirements.txt`: Python dependencies


## Features
- Modular design for each RAG technique
- FastAPI endpoints for integration
- Ready for deployment and extension
- **Single-point configuration** for:
	- Vector store (default: pgvector)
	- LLM provider/model (default: local Ollama, e.g., llama3.2)
	- Embeddings provider/model (default: local Ollama, e.g., nomic-embed-text:1.5)
- Easily switch between providers/models by editing `config.py` only

## Performance & Implementation Policy
**Compulsory:** All modules must use asynchronous execution and multithreading where applicable (e.g., multi-query rewriting, retrieval, LLM calls). Use Python's `asyncio` and `concurrent.futures.ThreadPoolExecutor` for parallel processing. API endpoints must be async and await module calls. This policy ensures optimal performance and scalability.

## Usage
Install dependencies and run the server:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Configuration
Edit `config.py` to change vector store, LLM, or embeddings provider/model. No other code changes required.

### Example config.py
```python
VECTOR_STORE_TYPE = 'pgvector'
PGVECTOR_CONN_STR = 'postgresql://user:password@localhost:5432/ragdb'
LLM_PROVIDER = 'ollama'
LLM_MODEL = 'llama3.2'
OLLAMA_BASE_URL = 'http://localhost:11434'
EMBEDDINGS_PROVIDER = 'ollama'
EMBEDDINGS_MODEL = 'nomic-embed-text:1.5'
```
