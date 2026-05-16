import os
import json
import time
from pinecone import Pinecone
from dotenv import load_dotenv
from .embedder import get_embedder

load_dotenv()

_pinecone_index = None


def get_index():
    global _pinecone_index
    if _pinecone_index is None:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        _pinecone_index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    return _pinecone_index


class Retriever:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def retrieve(self, query: str) -> dict:
        """
        Embed the query, search Pinecone, return top-k chunks with metadata.
        Returns: { "chunks": [...], "sources": [...], "retrieval_ms": int }
        """
        embedder = get_embedder()
        index = get_index()

        start = time.time()
        query_vector = embedder.embed_query(query)

        results = index.query(
            vector=query_vector,
            top_k=self.top_k,
            include_metadata=True,
        )
        elapsed_ms = int((time.time() - start) * 1000)

        chunks = []
        sources = set()

        for match in results.matches:
            meta = match.metadata or {}
            chunks.append(meta.get("text", ""))
            source = meta.get("source", "Unknown")
            if source != "Unknown":
                sources.add(source)

        return {
            "chunks": chunks,
            "sources": list(sources),
            "retrieval_ms": elapsed_ms,
            "chunks_used": len(chunks),
        }

    def build_context(self, chunks: list[str]) -> str:
        return "\n\n---\n\n".join(chunk for chunk in chunks if chunk.strip())
