# summarize_chat.py
import asyncio
import aiohttp
from typing import List, Dict
from .. import config

async def summarize_chat_context(chat_history: List[Dict], user_prompt: str, initial_response: str) -> str:
    """
    Summarize chat context if it exceeds LLM context limit. Takes chat history, latest user prompt, and initial response.
    Returns a summarized context string.
    """
    # Concatenate chat history
    history_text = '\n'.join([f"User: {msg['user']}\nPrompt: {msg['prompt']}\nResponse: {msg['response']}" for msg in chat_history])
    prompt = f"""The following is a long chat history between a user and an assistant. Summarize the conversation so far, keeping all important context for future questions.\n\nChat History:\n{history_text}\n\nLatest User Prompt: {user_prompt}\nLatest Response: {initial_response}\n\nSummarized Context:"""
    if config.LLM_PROVIDER == 'ollama':
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": config.LLM_MODEL,
                    "prompt": prompt
                }
            ) as response:
                result = await response.json()
                return result.get('response', '').strip()
    # Fallback: return truncated history
    return history_text[-config.LLM_CONTEXT_LIMIT:]

# Usage:
# summary = await summarize_chat_context(chat_history, user_prompt, initial_response)
