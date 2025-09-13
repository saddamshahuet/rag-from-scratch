from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import uvicorn
import logging
from datetime import datetime

# Import all modules
from modules.retrieval import retrieve_documents
from modules.decomposition import decompose_query
from modules.multiquery import generate_multiple_queries
from modules.fusion import reciprocal_rank_fusion
from modules.generation import generate_response
from modules.postretrieval import postprocess_context
from modules.initial_response import generate_initial_response
from modules.suggested_questions import generate_suggested_questions
from modules.final_response import combine_final_response
from modules.database import db_manager
from modules.response_evaluator import evaluate_response
from modules.session_manager import session_manager
from modules.summarize_chat import summarize_chat_context
import config

# Initialize FastAPI app
app = FastAPI(title="Combined RAG API", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    documents: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    user_id: str
    suggested_questions: List[str]
    evaluation_score: float
    processing_time: float

@app.on_event("startup")
async def startup_event():
    """Initialize database and session manager on startup"""
    await db_manager.create_connection_pool()
    await db_manager.create_tables()
    logger.info("Database initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db_manager.close_connection_pool()
    logger.info("Database connections closed")

@app.get('/')
async def root():
    return {'message': 'Combined RAG API is running with intelligent session management.'}

@app.post('/chat', response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main chat endpoint with intelligent session management and response evaluation
    """
    start_time = datetime.now()
    
    # Generate IDs if not provided
    user_id = request.user_id or str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Ensure user exists
        await db_manager.create_user(user_id)
        
        # Ensure session exists
        await db_manager.create_session(user_id, session_id)
        
        # Get intelligent session context
        session_context = await session_manager.get_session_context(user_id, session_id)
        
        # Execute combined RAG pipeline
        response = await execute_combined_rag(request.query, request.documents, session_context)
        
        # Evaluate response quality
        evaluation_score = await evaluate_response(request.query, response)
        
        # Generate suggested questions
        suggested = await generate_suggested_questions(request.query, response)
        
        # Store interaction in database
        await db_manager.add_chat_message(
            session_id=session_id,
            user_query=request.query,
            llm_response=response,
            evaluation_score=evaluation_score
        )
        
        # Update session context in memory
        await session_manager.update_session_context(session_id, request.query, response)
        
        # Schedule memory cleanup if needed
        if await session_manager.should_cleanup():
            background_tasks.add_task(session_manager.cleanup_memory)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            user_id=user_id,
            suggested_questions=suggested,
            evaluation_score=evaluation_score,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_combined_rag(query: str, documents: Optional[List[str]] = None, session_context: str = "") -> str:
    """
    Execute the complete combined RAG pipeline with all techniques
    """
    try:
        # Step 1: Query decomposition
        decomposed_queries = await decompose_query(query)
        
        # Step 2: Multi-query generation
        multiple_queries = await generate_multiple_queries(query)
        
        # Combine all queries
        all_queries = [query] + decomposed_queries + multiple_queries
        
        # Step 3: Retrieve documents for all queries
        all_retrieved_docs = []
        for q in all_queries:
            docs = await retrieve_documents(q, documents)
            all_retrieved_docs.extend(docs)
        
        # Step 4: Apply reciprocal rank fusion
        fused_docs = await reciprocal_rank_fusion(all_retrieved_docs, all_queries)
        
        # Step 5: Post-processing
        processed_context = await postprocess_context(fused_docs, query)
        
        # Step 6: Include session context if available
        full_context = f"{session_context}\n\n{processed_context}" if session_context else processed_context
        
        # Step 7: Generate final response
        response = await generate_response(query, full_context)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in combined RAG execution: {str(e)}")
        return f"I apologize, but I encountered an error processing your request: {str(e)}"

@app.get('/sessions/{user_id}')
async def get_user_sessions(user_id: str):
    """Get all sessions for a user"""
    try:
        sessions = await db_manager.get_user_sessions(user_id)
        return {"user_id": user_id, "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/sessions/{session_id}/history')
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = await db_manager.get_chat_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/sessions/{session_id}/summarize')
async def summarize_session(session_id: str):
    """Generate a summary of the session"""
    try:
        history = await db_manager.get_chat_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Session not found or empty")
        
        summary = await summarize_chat_context(history, "", "")
        return {"session_id": session_id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete('/sessions/{session_id}')
async def delete_session(session_id: str):
    """Delete a session and its history"""
    try:
        await db_manager.delete_session(session_id)
        # Remove from memory if cached
        if session_id in session_manager.active_sessions:
            del session_manager.active_sessions[session_id]
        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/cleanup')
async def manual_cleanup():
    """Manual trigger for memory cleanup"""
    try:
        await session_manager.cleanup_memory()
        return {"message": "Memory cleanup completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(session_manager.active_sessions)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
