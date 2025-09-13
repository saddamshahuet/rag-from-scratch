# database.py - Modular database management
import asyncio
import asyncpg
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from . import config

class DatabaseManager:
    def __init__(self):
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool and create tables"""
        self.pool = await asyncpg.create_pool(config.DATABASE_URL)
        await self.create_tables()
    
    async def create_tables(self):
        """Create all necessary tables"""
        async with self.pool.acquire() as conn:
            # Users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id VARCHAR PRIMARY KEY,
                    user_id VARCHAR REFERENCES users(user_id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    status VARCHAR DEFAULT 'active'
                )
            """)
            
            # Messages table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id SERIAL PRIMARY KEY,
                    session_id VARCHAR REFERENCES chat_sessions(session_id),
                    user_id VARCHAR REFERENCES users(user_id),
                    user_query TEXT NOT NULL,
                    llm_response TEXT NOT NULL,
                    response_score FLOAT,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB
                )
            """)
            
            # Sub-questions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS query_decomposition (
                    decomposition_id SERIAL PRIMARY KEY,
                    message_id INTEGER REFERENCES chat_messages(message_id),
                    original_query TEXT NOT NULL,
                    sub_questions JSONB NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
    
    async def create_user(self, user_id: str):
        """Create or update user"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id) VALUES ($1)
                ON CONFLICT (user_id) DO UPDATE SET last_active = NOW()
            """, user_id)
    
    async def create_session(self, session_id: str, user_id: str):
        """Create a new chat session"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_sessions (session_id, user_id) VALUES ($1, $2)
                ON CONFLICT (session_id) DO UPDATE SET last_active = NOW()
            """, session_id, user_id)
    
    async def save_message(self, session_id: str, user_id: str, user_query: str, 
                          llm_response: str, response_score: float = None, 
                          metadata: Dict = None) -> int:
        """Save chat message and return message_id"""
        async with self.pool.acquire() as conn:
            message_id = await conn.fetchval("""
                INSERT INTO chat_messages 
                (session_id, user_id, user_query, llm_response, response_score, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING message_id
            """, session_id, user_id, user_query, llm_response, response_score, 
            json.dumps(metadata) if metadata else None)
            return message_id
    
    async def save_decomposition(self, message_id: int, original_query: str, sub_questions: List[str]):
        """Save query decomposition"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO query_decomposition (message_id, original_query, sub_questions)
                VALUES ($1, $2, $3)
            """, message_id, original_query, json.dumps(sub_questions))
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_query, llm_response, response_score, timestamp, metadata
                FROM chat_messages 
                WHERE session_id = $1 
                ORDER BY timestamp DESC 
                LIMIT $2
            """, session_id, limit)
            return [dict(row) for row in reversed(rows)]
    
    async def update_session_activity(self, session_id: str):
        """Update session last activity"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE chat_sessions SET last_active = NOW() WHERE session_id = $1
            """, session_id)
    
    async def cleanup_inactive_sessions(self, timeout_seconds: int):
        """Clean up inactive sessions"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE chat_sessions SET status = 'inactive' 
                WHERE last_active < NOW() - INTERVAL '%s seconds'
                AND status = 'active'
            """, timeout_seconds)

# Global database manager instance
db_manager = DatabaseManager()
