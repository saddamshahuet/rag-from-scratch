# retrieval.py
def retrieve(queries: List[str]) -> List[str]:
import asyncio
import aiohttp
import psycopg2
from typing import List
from .. import config

# Use pgvector and local embedding model for retrieval
async def retrieve(queries: List[str]) -> List[List[str]]:
    """
    Asynchronously retrieve relevant documents for each query using pgvector and the configured embedding model.
    Returns a list of lists of documents (one list per query).
    """
    conn = psycopg2.connect(config.PGVECTOR_CONN_STR)
    cursor = conn.cursor()

    async def embed_and_retrieve(query):
        embedding = []
        if config.EMBEDDINGS_PROVIDER == 'ollama':
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{config.OLLAMA_BASE_URL}/api/embeddings",
                    json={
                        "model": config.EMBEDDINGS_MODEL,
                        "prompt": query
                    }
                ) as emb_response:
                    emb_json = await emb_response.json()
                    embedding = emb_json.get('embedding', [])
        # Query pgvector for similar documents
        cursor.execute(
            """
            SELECT content FROM documents ORDER BY embedding <-> %s LIMIT 5;
            """,
            (embedding,)
        )
        docs = [row[0] for row in cursor.fetchall()]
        return docs

    tasks = [embed_and_retrieve(q) for q in queries]
    results = await asyncio.gather(*tasks)
    cursor.close()
    conn.close()
    return results
