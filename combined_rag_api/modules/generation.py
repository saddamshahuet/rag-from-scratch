# generation.py
def generate(docs: List[str], query: str) -> str:
import asyncio
import aiohttp
from typing import List
from .. import config

# Use local LLM (Ollama or transformers) for answer synthesis
async def generate(docs: List[str], query: str) -> str:
    """
    Asynchronously generate an answer using the configured LLM provider/model, given the fused context and query.
    """
    context = '\n\n'.join(docs)
    prompt = f"""Answer the following question based only on the provided context.\n\nContext:\n{context}\n\nQuestion: {query}"""

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
