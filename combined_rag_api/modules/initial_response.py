# initial_response.py
import asyncio
import aiohttp
from typing import List
from .. import config

async def initial_response(docs: List[dict], query: str) -> str:
    """
    Generate an initial response by summarizing the context from related documents and answering the user query using the configured LLM.
    """
    context = '\n\n'.join(doc['content'] for doc in docs)
    prompt = f"""Summarize the following context and answer the question.\n\nContext:\n{context}\n\nQuestion: {query}"""
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
    # Fallback: return context and query
    return f"[No LLM configured] Context: {context}\nQuestion: {query}"

# Usage:
# response = await initial_response(related_chunks, query)
