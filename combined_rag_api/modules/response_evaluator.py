# response_evaluator.py
import asyncio
import aiohttp
from typing import Dict
from .. import config

async def evaluate_response(query: str, response: str, context: str) -> float:
    """
    Evaluate LLM response quality using configured evaluation LLM.
    Returns a score between 0.0 and 1.0.
    """
    prompt = f"""
    Evaluate the quality of the following response to a user query based on the given context.
    Rate the response on a scale of 0.0 to 1.0 considering:
    - Relevance to the query
    - Accuracy based on context
    - Completeness of the answer
    - Clarity and coherence
    
    Query: {query}
    Context: {context}
    Response: {response}
    
    Provide only a numeric score (0.0-1.0):
    """
    
    if config.EVALUATION_LLM_PROVIDER == 'ollama':
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": config.EVALUATION_LLM_MODEL,
                    "prompt": prompt
                }
            ) as resp:
                result = await resp.json()
                try:
                    score_text = result.get('response', '0.0').strip()
                    # Extract first number found in response
                    import re
                    numbers = re.findall(r'\d+\.?\d*', score_text)
                    if numbers:
                        score = float(numbers[0])
                        return min(max(score, 0.0), 1.0)  # Clamp between 0.0-1.0
                except (ValueError, IndexError):
                    pass
    
    # Fallback scoring based on response length and query match
    query_words = set(query.lower().split())
    response_words = set(response.lower().split())
    overlap = len(query_words & response_words) / max(len(query_words), 1)
    length_score = min(len(response) / 500, 1.0)  # Longer responses up to 500 chars
    return (overlap * 0.6 + length_score * 0.4)

# Usage:
# score = await evaluate_response(query, response, context)
