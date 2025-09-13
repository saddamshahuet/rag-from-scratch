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

## 🏗️ Architecture

```
combined_rag_api/
├── main.py                    # FastAPI application
├── config.py                  # Centralized configuration  
├── requirements.txt           # Dependencies
└── modules/
    ├── retrieval.py          # Document retrieval
    ├── decomposition.py      # Query decomposition
    ├── multiquery.py         # Multi-query generation
    ├── fusion.py             # Reciprocal rank fusion
    ├── generation.py         # Response generation
    ├── database.py           # Database management
    ├── response_evaluator.py # Response evaluation
    ├── session_manager.py    # Session & memory management
    └── ...                   # Other modules
```

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
