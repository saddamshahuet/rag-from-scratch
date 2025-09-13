# postretrieval.py
import asyncio
from typing import List, Dict

async def expand_chunks(retrieved_chunks: List[Dict], vectorstore: List[Dict]) -> List[Dict]:
    """
    Given retrieved chunks (each with metadata including 'doc_id'),
    return all chunks from vectorstore that share any doc_id with the retrieved chunks.
    """
    doc_ids = set(chunk['metadata']['doc_id'] for chunk in retrieved_chunks)
    # Simulate async filtering (replace with DB query in production)
    def filter_related():
        return [chunk for chunk in vectorstore if chunk['metadata']['doc_id'] in doc_ids]
    loop = asyncio.get_event_loop()
    related_chunks = await loop.run_in_executor(None, filter_related)
    return related_chunks

# Usage:
# related_chunks = await expand_chunks(retrieved_chunks, vectorstore)
# (retrieved_chunks and vectorstore should be lists of dicts with 'metadata')
