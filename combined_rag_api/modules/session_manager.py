# session_manager.py - Intelligent session and memory management
import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone
from .database import db_manager
from .. import config

class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}  # In-memory cache for active sessions
        self.last_cleanup = time.time()
    
    async def get_session_context(self, user_id: str, session_id: str) -> str:
        """
        Intelligently load session context into memory with summarization if needed.
        Returns processed context that fits within LLM token limits.
        """
        # Check if session is in memory
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].get('context', '')
        
        # Load from database
        chat_history = await db_manager.get_chat_history(session_id)
        
        if not chat_history:
            return ''
        
        # Build full context
        full_context = self._build_context_string(chat_history)
        
        # Check if context exceeds threshold
        if len(full_context) > config.SUMMARIZATION_THRESHOLD:
            # Apply recursive summarization
            summarized_context = await self._recursive_summarization(chat_history)
            context = summarized_context
        else:
            context = full_context
        
        # Cache in memory
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'context': context,
            'last_access': time.time(),
            'message_count': len(chat_history)
        }
        
        return context
    
    async def _recursive_summarization(self, chat_history: List[Dict]) -> str:
        """
        Recursively summarize chat history until it fits within context limits.
        """
        from .summarize_chat import summarize_chat_context
        
        # Split history into chunks
        chunk_size = 10  # Number of messages per chunk
        chunks = [chat_history[i:i + chunk_size] for i in range(0, len(chat_history), chunk_size)]
        
        summaries = []
        for chunk in chunks:
            if len(chunk) > 1:
                # Create pseudo query and response for summarization
                chunk_text = self._build_context_string(chunk)
                if len(chunk_text) > config.SUMMARIZATION_THRESHOLD:
                    summary = await summarize_chat_context(chunk, "", "")
                    summaries.append(summary)
                else:
                    summaries.append(chunk_text)
            else:
                summaries.append(self._build_context_string(chunk))
        
        # Combine summaries
        combined = '\n\n'.join(summaries)
        
        # If still too long, summarize again
        if len(combined) > config.SUMMARIZATION_THRESHOLD:
            # Create final summary
            final_summary = await summarize_chat_context(
                [{'user': 'system', 'prompt': 'Combined summaries', 'response': combined}],
                "", ""
            )
            return final_summary
        
        return combined
    
    def _build_context_string(self, chat_history: List[Dict]) -> str:
        """Build context string from chat history"""
        return '\n'.join([
            f"User: {msg['user_query']}\nAssistant: {msg['llm_response']}"
            for msg in chat_history
        ])
    
    async def update_session_context(self, session_id: str, new_query: str, new_response: str):
        """Update session context with new interaction"""
        if session_id in self.active_sessions:
            current_context = self.active_sessions[session_id]['context']
            new_entry = f"\nUser: {new_query}\nAssistant: {new_response}"
            updated_context = current_context + new_entry
            
            # Check if context is getting too long
            if len(updated_context) > config.MAX_CONTEXT_LENGTH:
                # Trigger summarization
                chat_history = await db_manager.get_chat_history(session_id)
                summarized = await self._recursive_summarization(chat_history)
                self.active_sessions[session_id]['context'] = summarized
            else:
                self.active_sessions[session_id]['context'] = updated_context
            
            self.active_sessions[session_id]['last_access'] = time.time()
    
    async def cleanup_memory(self):
        """Clean up inactive sessions from memory"""
        current_time = time.time()
        inactive_sessions = [
            session_id for session_id, data in self.active_sessions.items()
            if current_time - data['last_access'] > config.SESSION_TIMEOUT
        ]
        
        for session_id in inactive_sessions:
            del self.active_sessions[session_id]
        
        # Update database
        await db_manager.cleanup_inactive_sessions(config.SESSION_TIMEOUT)
        
        self.last_cleanup = current_time
    
    async def should_cleanup(self) -> bool:
        """Check if it's time for memory cleanup"""
        return time.time() - self.last_cleanup > config.MEMORY_CLEANUP_INTERVAL

# Global session manager
session_manager = SessionManager()
