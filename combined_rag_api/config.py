# LLM context limit for chat summarization
LLM_CONTEXT_LIMIT = int(os.getenv('LLM_CONTEXT_LIMIT', '4096'))
import os

# Vector store config
VECTOR_STORE_TYPE = os.getenv('VECTOR_STORE_TYPE', 'pgvector')  # Options: 'pgvector', 'chromadb', etc.
PGVECTOR_CONN_STR = os.getenv('PGVECTOR_CONN_STR', 'postgresql://user:password@localhost:5432/ragdb')

# LLM config
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')  # Options: 'ollama', 'transformers', 'openai'
LLM_MODEL = os.getenv('LLM_MODEL', 'llama3.2')      # Example: 'llama3.2', 'gpt-3.5-turbo', etc.
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# Embeddings config
EMBEDDINGS_PROVIDER = os.getenv('EMBEDDINGS_PROVIDER', 'ollama')  # Options: 'ollama', 'transformers', 'openai'
EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL', 'nomic-embed-text:1.5')

# API keys (if needed)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<your-openai-key>')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY', '<your-langchain-key>')
