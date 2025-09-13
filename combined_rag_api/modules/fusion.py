# fusion.py
def fuse(docs: List[List[str]]) -> List[str]:
from typing import List
import asyncio

# Reciprocal Rank Fusion (RRF) for combining multiple ranked lists
async def fuse(docs: List[List[str]], k: int = 60) -> List[str]:
    """
    Asynchronously fuse multiple lists of ranked documents using reciprocal rank fusion.
    Returns a reranked list of unique documents.
    """
    fused_scores = {}
    for doc_list in docs:
        for rank, doc in enumerate(doc_list):
            if doc not in fused_scores:
                fused_scores[doc] = 0
            fused_scores[doc] += 1 / (rank + k)
    # Sort by fused score
    reranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in reranked]
