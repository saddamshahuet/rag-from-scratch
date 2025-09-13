# multiquery.py
def rewrite(questions: List[str]) -> List[str]:
import asyncio
import aiohttp
from typing import List
from .. import config

# Use local LLM (Ollama or transformers) for multi-query rewriting
async def rewrite(questions: List[str]) -> List[str]:
    """
    Asynchronously rewrite each question into multiple perspectives using the configured LLM provider/model.
    Returns a list of rewritten queries for all input questions.
    """
    rewritten = []
    if config.LLM_PROVIDER == 'ollama':
        async def rewrite_one(q):
            prompt = f"""You are an AI language model assistant. Your task is to generate five different versions of the given user question to retrieve relevant documents from a vector database. By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of the distance-based similarity search. Provide these alternative questions separated by newlines. Original question: {q}"""
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": config.LLM_MODEL,
                        "prompt": prompt
                    }
                ) as response:
                    result = await response.json()
                    return [qq.strip() for qq in result.get('response', '').split('\n') if qq.strip()]
        # Run all rewrites in parallel
        tasks = [rewrite_one(q) for q in questions]
        all_rewritten = await asyncio.gather(*tasks)
        for rewritten_list in all_rewritten:
            rewritten.extend(rewritten_list)
    # Fallback: return original questions only
    if not rewritten:
        rewritten = questions
    return rewritten
