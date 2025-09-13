# final_response.py
from typing import List

async def final_response(initial: str, suggestions: List[str]) -> str:
    """
    Concatenate initial response and suggested questions for final output.
    """
    suggestions_text = '\n'.join([f"- {q}" for q in suggestions])
    return f"{initial}\n\nSuggested Next Questions:\n{suggestions_text}"

# Usage:
# result = await final_response(initial_response, suggested_questions)
