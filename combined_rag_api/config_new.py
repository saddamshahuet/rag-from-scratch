import os

# Database config
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/ragdb')

# Vector store config
VECTOR_STORE_TYPE = os.getenv('VECTOR_STORE_TYPE', 'pgvector')  # Options: 'pgvector', 'chromadb', etc.
PGVECTOR_CONN_STR = os.getenv('PGVECTOR_CONN_STR', 'postgresql://user:password@localhost:5432/ragdb')

# LLM config per module/phase
DECOMPOSITION_LLM_PROVIDER = os.getenv('DECOMPOSITION_LLM_PROVIDER', 'ollama')
DECOMPOSITION_LLM_MODEL = os.getenv('DECOMPOSITION_LLM_MODEL', 'llama3.2')

MULTIQUERY_LLM_PROVIDER = os.getenv('MULTIQUERY_LLM_PROVIDER', 'ollama')
MULTIQUERY_LLM_MODEL = os.getenv('MULTIQUERY_LLM_MODEL', 'llama3.2')

RESPONSE_LLM_PROVIDER = os.getenv('RESPONSE_LLM_PROVIDER', 'ollama')
RESPONSE_LLM_MODEL = os.getenv('RESPONSE_LLM_MODEL', 'llama3.2')

EVALUATION_LLM_PROVIDER = os.getenv('EVALUATION_LLM_PROVIDER', 'ollama')
EVALUATION_LLM_MODEL = os.getenv('EVALUATION_LLM_MODEL', 'llama3.2')

SUMMARIZATION_LLM_PROVIDER = os.getenv('SUMMARIZATION_LLM_PROVIDER', 'ollama')
SUMMARIZATION_LLM_MODEL = os.getenv('SUMMARIZATION_LLM_MODEL', 'llama3.2')

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# Embeddings config
EMBEDDINGS_PROVIDER = os.getenv('EMBEDDINGS_PROVIDER', 'ollama')  # Options: 'ollama', 'transformers', 'openai'
EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL', 'nomic-embed-text:1.5')

# Session management config
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '1800'))  # 30 minutes
MEMORY_CLEANUP_INTERVAL = int(os.getenv('MEMORY_CLEANUP_INTERVAL', '300'))  # 5 minutes
MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '4096'))
SUMMARIZATION_THRESHOLD = int(os.getenv('SUMMARIZATION_THRESHOLD', '3200'))  # 80% of max context

# API keys (if needed)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<your-openai-key>')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY', '<your-langchain-key>')

# Legacy compatibility
LLM_PROVIDER = RESPONSE_LLM_PROVIDER
LLM_MODEL = RESPONSE_LLM_MODEL
LLM_CONTEXT_LIMIT = MAX_CONTEXT_LENGTH
