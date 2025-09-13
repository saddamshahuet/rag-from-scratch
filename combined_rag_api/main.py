from fastapi import FastAPI, Request
from modules import retrieval, multiquery, fusion, decomposition, generation, postretrieval, initial_response, suggested_questions, final_response, summarize_chat
import asyncio
from typing import Dict, List

app = FastAPI()

# In-memory session and chat management (replace with DB for production)
user_sessions: Dict[str, Dict[str, List[Dict]]] = {}  # user_id -> session_id -> chat_history

@app.get('/')
async def root():
    return {'message': 'Combined RAG API is running.'}

@app.post('/chat')
async def chat(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    session_id = data.get('session_id')
    query = data.get('query')
    vectorstore = data.get('vectorstore', [])  # Should be replaced with DB fetch

    # Initialize user/session
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    if session_id not in user_sessions[user_id]:
        user_sessions[user_id][session_id] = []

    # Modular async pipeline
    sub_questions = await decomposition.decompose(query)
    queries = await multiquery.rewrite(sub_questions)
    docs = await retrieval.retrieve(queries)
    # Post-retrieval expansion
    related_chunks = await postretrieval.expand_chunks(docs, vectorstore)
    # Initial response
    initial = await initial_response.initial_response(related_chunks, query)
    # Suggested questions
    suggestions = await suggested_questions.suggest_questions(query, related_chunks, initial)
    # Final response
    final = await final_response.final_response(initial, suggestions)

    # Maintain chat history
    chat_entry = {
        'user': user_id,
        'prompt': query,
        'response': final
    }
    user_sessions[user_id][session_id].append(chat_entry)

    # Summarize chat context if too long
    chat_history = user_sessions[user_id][session_id]
    history_text = '\n'.join([f"User: {msg['user']}\nPrompt: {msg['prompt']}\nResponse: {msg['response']}" for msg in chat_history])
    if len(history_text) > generation.config.LLM_CONTEXT_LIMIT:
        summary = await summarize_chat.summarize_chat_context(chat_history, query, initial)
        user_sessions[user_id][session_id] = [{'user': user_id, 'prompt': 'SUMMARY', 'response': summary}]

    return {
        'final_response': final,
        'initial_response': initial,
        'suggested_questions': suggestions,
        'chat_history': user_sessions[user_id][session_id]
    }
