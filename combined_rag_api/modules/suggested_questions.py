# suggested_questions.py
import asyncio
import aiohttp
from typing import List
from .. import config

async def suggest_questions(query: str, docs: List[dict], response: str) -> List[str]:
    """
    Suggest possible next questions or hints for the user based on the original query, relevant document context, and the generated response.
    """
    context = '\n\n'.join(doc['content'] for doc in docs)
    prompt = f"""Given the following user query, context, and response, suggest 3 possible follow-up questions or hints the user might ask next.\n\nUser Query: {query}\n\nContext:\n{context}\n\nResponse:\n{response}\n\nSuggestions:"""
    if config.LLM_PROVIDER == 'ollama':
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": config.LLM_MODEL,
                    "prompt": prompt
                }
            ) as resp:
                result = await resp.json()
                return [q.strip() for q in result.get('response', '').split('\n') if q.strip()]
    # Fallback: return empty list
    return []

# Usage:
# suggestions = await suggest_questions(query, related_chunks, response)
