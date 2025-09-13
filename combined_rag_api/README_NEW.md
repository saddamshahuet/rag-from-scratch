# Combined RAG System with Intelligent Session Management

A production-ready FastAPI application that combines multiple RAG (Retrieval-Augmented Generation) techniques with intelligent session management, database integration, and response evaluation.

## 🚀 Features

### Core RAG Techniques
- **Query Decomposition**: Break complex queries into sub-questions
- **Multi-Query Generation**: Generate diverse query variations  
- **Reciprocal Rank Fusion**: Combine and rank retrieved documents
- **Post-Processing**: Context refinement and optimization
- **Response Generation**: LLM-powered answer generation

### 🧠 Intelligent Session Management
- **Memory-Based Caching**: Active sessions stored in memory for fast access
- **Automatic Summarization**: Recursive summarization when context exceeds limits
- **Intelligent Loading**: Smart session context retrieval from database
- **Memory Cleanup**: Automatic cleanup of inactive sessions

### 💾 Database Integration
- **PostgreSQL Support**: Full async database operations with pgvector
- **User Management**: User registration and session tracking
- **Chat History**: Persistent conversation storage
- **Query Analysis**: Store and analyze query decomposition patterns

### 📊 Response Evaluation
- **LLM-Based Scoring**: Automatic response quality assessment (0.0-1.0)
- **Multi-Criteria Evaluation**: Relevance, accuracy, completeness scoring
- **Performance Metrics**: Processing time and evaluation tracking

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 13+ with pgvector extension
- Ollama (for local LLM inference)

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama (in separate terminal)
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text:1.5

# Run the application
python main.py
```

The API will be available at `http://localhost:8000`

## 📡 API Usage

### Main Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
    "query": "What is the impact of AI on healthcare?",
    "user_id": "user123",
    "session_id": "session456"
}
```

**Response:**
```json
{
    "response": "AI has significant impact on healthcare including...",
    "session_id": "session456", 
    "user_id": "user123",
    "suggested_questions": ["What are the challenges?", "How about privacy?"],
    "evaluation_score": 0.85,
    "processing_time": 2.34
}
```

### Session Management
- `GET /sessions/{user_id}` - Get all sessions for a user
- `GET /sessions/{session_id}/history` - Get chat history
- `POST /sessions/{session_id}/summarize` - Generate session summary
- `DELETE /sessions/{session_id}` - Delete session

### Utility Endpoints
- `GET /health` - Health check and active session count
- `POST /cleanup` - Manual memory cleanup

### Document Processing and Embedding API

This extension to the Combined RAG API provides comprehensive document processing and embedding capabilities for various file formats and web content.

#### Features

- **Multi-format Document Processing**: Support for PDF, DOCX, DOC, TXT, MD, HTML, XLS, XLSX, and more
- **URL Content Extraction**: Extract and process content from web URLs
- **Vector Store Management**: Create, update, and manage vector stores
- **Embedding Operations**: Generate embeddings with various models
- **System Configuration**: Manage defaults and settings

#### API Endpoints

##### Document Processing

- `POST /api/documents/upload`: Upload and process document files
- `POST /api/documents/url`: Extract and process content from URLs
- `GET /api/documents/{document_id}`: Check document processing status
- `DELETE /api/documents/{document_id}`: Delete a document and its embeddings

##### Vector Store Management

- `GET /api/vectorstores`: List all vector stores
- `POST /api/vectorstores`: Create a new vector store
- `GET /api/vectorstores/{store_id}`: Get vector store details
- `PUT /api/vectorstores/{store_id}`: Update a vector store
- `DELETE /api/vectorstores/{store_id}`: Delete a vector store
- `GET /api/vectorstores/{store_id}/documents`: List documents in a vector store

##### Embedding Operations

- `POST /api/embed`: Generate embeddings for texts
- `POST /api/embed/batch`: Batch generate embeddings
- `GET /api/embed/models`: List available embedding models
- `POST /api/embed/models/default`: Set the default embedding model

##### Configuration

- `GET /api/config`: Get all configuration settings
- `PUT /api/config`: Update a configuration setting
- `GET /api/config/defaults`: Get default processing settings
- `PUT /api/config/defaults`: Set default processing settings

## Usage Examples

### Upload and Process a Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -F "vector_store_id=1" \
  -F "embedding_model=sentence-transformers/all-MiniLM-L6-v2" \
  -F "chunk_size=1000" \
  -F "chunk_overlap=200" \
  -F "metadata={\"category\":\"technical\",\"author\":\"John Doe\"}"
```

### Process Content from a URL

```bash
curl -X POST "http://localhost:8000/api/documents/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "vector_store_id": 1,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "metadata": {
      "category": "web",
      "source": "example.com"
    }
  }'
```

### Create a New Vector Store

```bash
curl -X POST "http://localhost:8000/api/vectorstores" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technical Documentation",
    "description": "Vector store for technical documents",
    "store_type": "pgvector",
    "connection_params": {
      "host": "localhost",
      "port": 5432,
      "database": "vectordb",
      "user": "postgres",
      "password": "password"
    }
  }'
```

### Generate Embeddings

```bash
curl -X POST "http://localhost:8000/api/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["This is a sample text", "Another example text"],
    "model": "sentence-transformers/all-MiniLM-L6-v2"
  }'
```

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Start the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Access the API documentation at http://localhost:8000/docs

## Configuration

The API can be configured through environment variables or the configuration API endpoints. Key settings include:

- `DEFAULT_EMBEDDING_MODEL`: Default model for generating embeddings
- `DEFAULT_VECTOR_STORE_ID`: Default vector store for storing embeddings
- `CHUNK_SIZE`: Default chunk size for document processing
- `CHUNK_OVERLAP`: Default chunk overlap for document processing

## ⚙️ Configuration

Key configuration options in `config.py`:

```python
# Database
DATABASE_URL = "postgresql://user:password@localhost:5432/rag_db"

# LLM Models (configurable per module)
DECOMPOSITION_LLM_MODEL = "llama3.2"
RESPONSE_LLM_MODEL = "llama3.2" 
EVALUATION_LLM_MODEL = "llama3.2"

# Session Management
SESSION_TIMEOUT = 1800  # 30 minutes
MAX_CONTEXT_LENGTH = 8000
SUMMARIZATION_THRESHOLD = 6000
MEMORY_CLEANUP_INTERVAL = 300  # 5 minutes
```

## 🎯 Key Features Explained

### Intelligent Session Management
- **Smart Loading**: Automatically loads relevant chat history into memory
- **Recursive Summarization**: Compresses long conversations while preserving context
- **Memory Optimization**: Keeps active sessions in memory for fast access
- **Auto Cleanup**: Removes inactive sessions based on configurable timeout

### Response Evaluation
- **Quality Scoring**: Each response gets a 0.0-1.0 quality score
- **Multi-Factor Assessment**: Evaluates relevance, accuracy, and completeness
- **Performance Tracking**: Monitor response quality and processing time

### Database Schema
```sql
-- Core tables for users, sessions, messages, and query analysis
CREATE TABLE users (user_id VARCHAR(255) PRIMARY KEY, ...);
CREATE TABLE chat_sessions (session_id VARCHAR(255) PRIMARY KEY, ...);
CREATE TABLE chat_messages (id SERIAL PRIMARY KEY, ...);
CREATE TABLE query_decomposition (id SERIAL PRIMARY KEY, ...);
```

## 🚀 Production Ready

- **Async Operations**: All I/O operations are asynchronous
- **Connection Pooling**: Efficient database connection management
- **Background Tasks**: Non-critical operations run in background
- **Structured Logging**: Comprehensive logging throughout
- **Health Monitoring**: Real-time system health checks

## 📈 Performance Optimizations

1. **Memory Caching**: Active sessions cached for instant access
2. **Smart Summarization**: Context compression when needed
3. **Parallel Processing**: Concurrent query processing where possible
4. **Background Cleanup**: Automatic memory management
5. **Connection Pooling**: Efficient database operations

## 🔧 Development

The system is designed for easy extension:
- Add new RAG techniques as modules
- Configure different LLM models per module
- Extend database schema for new features
- Add custom evaluation criteria

## 📄 License

MIT License - see LICENSE file for details.

# Document Processing and Embedding API

This extension to the Combined RAG API provides comprehensive document processing and embedding capabilities for various file formats and web content.

## Features

- **Multi-format Document Processing**: Support for PDF, DOCX, TXT, MD, HTML, XLS, XLSX, and more
- **URL Content Extraction**: Extract and process content from web URLs with link following capabilities
- **Vector Store Management**: Create, update, and manage vector stores
- **Embedding Operations**: Generate embeddings with various models
- **System Configuration**: Manage defaults and settings

## Supported Document Formats

- **PDF**: Adobe PDF documents (.pdf)
- **Word**: Microsoft Word documents (.docx)
- **Text**: Plain text files (.txt) and Markdown (.md, .markdown)
- **HTML**: Web pages (.html, .htm)
- **Excel**: Microsoft Excel spreadsheets (.xlsx, .xls)
- **Web Content**: URL-based content extraction with link following

## API Endpoints

### Document Processing

- `POST /api/documents/upload`: Upload and process document files
- `POST /api/documents/url`: Extract and process content from URLs
- `GET /api/documents/{document_id}`: Check document processing status
- `DELETE /api/documents/{document_id}`: Delete a document and its embeddings

### Vector Store Management

- `GET /api/vectorstores`: List all vector stores
- `POST /api/vectorstores`: Create a new vector store
- `GET /api/vectorstores/{store_id}`: Get vector store details
- `PUT /api/vectorstores/{store_id}`: Update a vector store
- `DELETE /api/vectorstores/{store_id}`: Delete a vector store
- `GET /api/vectorstores/{store_id}/documents`: List documents in a vector store

### Embedding Operations

- `POST /api/embed`: Generate embeddings for texts
- `POST /api/embed/batch`: Batch generate embeddings
- `GET /api/embed/models`: List available embedding models
- `POST /api/embed/models/default`: Set the default embedding model

### Configuration

- `GET /api/config`: Get all configuration settings
- `PUT /api/config`: Update a configuration setting
- `GET /api/config/defaults`: Get default processing settings
- `PUT /api/config/defaults`: Set default processing settings

## Usage Examples

### Upload and Process a Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -F "vector_store_id=1" \
  -F "embedding_model=sentence-transformers/all-MiniLM-L6-v2" \
  -F "chunk_size=1000" \
  -F "chunk_overlap=200" \
  -F "metadata={\"category\":\"technical\",\"author\":\"John Doe\"}"
```

### Process Content from a URL (with link following)

```bash
curl -X POST "http://localhost:8000/api/documents/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "vector_store_id": 1,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "follow_links": true,
    "max_depth": 2,
    "same_domain_only": true,
    "metadata": {
      "category": "web",
      "source": "example.com"
    }
  }'
```

### Create a New Vector Store

```bash
curl -X POST "http://localhost:8000/api/vectorstores" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technical Documentation",
    "description": "Vector store for technical documents",
    "store_type": "pgvector",
    "connection_params": {
      "host": "localhost",
      "port": 5432,
      "database": "vectordb",
      "user": "postgres",
      "password": "password"
    }
  }'
```

### Generate Embeddings

```bash
curl -X POST "http://localhost:8000/api/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["This is a sample text", "Another example text"],
    "model": "sentence-transformers/all-MiniLM-L6-v2"
  }'
```

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Start the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Access the API documentation at http://localhost:8000/docs

## Configuration

The API can be configured through environment variables or the configuration API endpoints. Key settings include:

- `DEFAULT_EMBEDDING_MODEL`: Default model for generating embeddings
- `DEFAULT_VECTOR_STORE_ID`: Default vector store for storing embeddings
- `CHUNK_SIZE`: Default chunk size for document processing
- `CHUNK_OVERLAP`: Default chunk overlap for document processing

## Extending Support for Additional File Formats

To add support for a new file format:

1. Create a new processor class that extends `DocumentProcessor`
2. Implement the `process` and `supports_format` methods
3. Register the processor in the `processors/__init__.py` file

Example:

```python
from embedding_vectorstore.document_processor import DocumentProcessor

class NewFormatProcessor(DocumentProcessor):
    def supports_format(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.new']
    
    async def process(self, file_path: str, metadata=None, chunk_size=1000, chunk_overlap=200):
        # Implementation for processing the new format
        pass
```

Then register it:

```python
# In processors/__init__.py
from embedding_vectorstore.processors.new_format_processor import NewFormatProcessor

available_processors = [
    # ... other processors
    NewFormatProcessor(),
]
```

## Advanced URL Processing

The URL processor supports crawling web pages and extracting content from linked pages:

- `follow_links`: Set to `true` to follow links on the page
- `max_depth`: Maximum depth for link following (1 = only the specified URL, 2 = also follow links from that page, etc.)
- `same_domain_only`: Restrict link following to the same domain as the original URL

This enables building comprehensive knowledge bases from websites by automatically extracting content from multiple linked pages.
