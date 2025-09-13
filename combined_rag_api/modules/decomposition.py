# decomposition.py
def decompose(query: str) -> List[str]:

from typing import List
from .. import config


# Use local LLM (Ollama or transformers) for decomposition
import asyncio
import aiohttp
from typing import List
from .. import config

async def decompose(query: str) -> List[str]:
    """
    Asynchronously decompose a complex query into sub-questions using the configured LLM provider/model.
    Returns a list of sub-questions (including the original).
    """
    prompt = f"""You are a helpful assistant that generates multiple sub-questions related to an input question.\nThe goal is to break down the input into a set of sub-problems / sub-questions that can be answered in isolation.\nGenerate multiple search queries related to: {query}\nOutput (3 queries):"""

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
                sub_questions = [q.strip() for q in result.get('response', '').split('\n') if q.strip()]
                if query not in sub_questions:
                    sub_questions.insert(0, query)
                return sub_questions
    # Fallback: return original query only
    return [query]
