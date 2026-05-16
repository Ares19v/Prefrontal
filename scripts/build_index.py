"""
build_index.py — Run once to ingest all knowledge into Pinecone.

Usage:
    cd c:\\Users\\Devansh Tyagi\\Desktop\\Projects\\Prefrontal
    python scripts/build_index.py

Sources ingested:
    1. knowledge_base/curated/seed.json  — 50 hand-written seed entries
    2. knowledge_base/books/*.pdf        — 4 evolutionary psychology books
"""

import os
import sys
import json
import uuid
import time

# Allow imports from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

# ── Config ────────────────────────────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX_NAME", "prefrontal-knowledge")
SEED_PATH        = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "curated", "seed.json")
BOOKS_DIR        = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "books")
BATCH_SIZE       = 64
CHUNK_SIZE       = 512
CHUNK_OVERLAP    = 64
QUERY_PREFIX     = "Represent this sentence for searching relevant passages: "

# ── Load model & index ────────────────────────────────
print("Loading embedding model (BAAI/bge-base-en-v1.5)...")
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

pc    = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)
print(f"Connected to Pinecone index: {PINECONE_INDEX}")


def embed_batch(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()


def upsert_batch(vectors: list[dict]):
    """Upsert with retry on rate limit."""
    for attempt in range(3):
        try:
            index.upsert(vectors=vectors)
            return
        except Exception as e:
            if attempt < 2:
                print(f"  Upsert failed ({e}), retrying in 5s...")
                time.sleep(5)
            else:
                raise


def ingest_seed():
    print("\n-- Ingesting seed.json ----------------------------------")
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)

    vectors = []
    for entry in tqdm(entries, desc="Seed entries"):
        # Combine all fields into one rich text chunk
        text = (
            f"Behavior: {entry['behavior']}\n"
            f"Modern Trigger: {entry['modern_trigger']}\n"
            f"Ancestral Mechanism: {entry['ancestral_mechanism']}\n"
            f"Brain Region: {entry['brain_region']}\n"
            f"Brain Chemistry: {entry['brain_chemistry']}\n"
            f"The Insight: {entry['the_insight']}"
        )
        embedding = embed_batch([text])[0]
        vectors.append({
            "id": entry["id"],
            "values": embedding,
            "metadata": {
                "text": text,
                "source": "Prefrontal Seed Data",
                "behavior": entry["behavior"],
                "tags": ", ".join(entry.get("tags", [])),
                "sources": ", ".join(entry.get("sources", [])),
            },
        })

        if len(vectors) >= BATCH_SIZE:
            upsert_batch(vectors)
            vectors = []

    if vectors:
        upsert_batch(vectors)

    print(f"  ✓ {len(entries)} seed entries ingested.")


def ingest_books():
    print("\n-- Ingesting PDF books ----------------------------------")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    book_meta = {
        "behave_sapolsky.pdf":            "Behave — Sapolsky",
        "why_zebras_sapolsky.pdf":        "Why Zebras Don't Get Ulcers — Sapolsky",
        "selfish_gene_dawkins.pdf":       "The Selfish Gene — Dawkins",
        "story_human_body_lieberman.pdf": "The Story of the Human Body — Lieberman",
    }

    for filename, source_name in book_meta.items():
        path = os.path.join(BOOKS_DIR, filename)
        if not os.path.exists(path):
            print(f"  ⚠ Not found, skipping: {filename}")
            continue

        print(f"  Loading {filename}...")
        loader = PyPDFLoader(path)
        pages  = loader.load()
        chunks = splitter.split_documents(pages)
        print(f"    → {len(pages)} pages → {len(chunks)} chunks")

        vectors = []
        for chunk in tqdm(chunks, desc=f"  {source_name[:30]}"):
            text = chunk.page_content.strip()
            if len(text) < 50:   # skip near-empty chunks
                continue
            embedding = embed_batch([text])[0]
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {
                    "text": text[:1000],   # Pinecone metadata limit
                    "source": source_name,
                    "page": chunk.metadata.get("page", 0),
                },
            })

            if len(vectors) >= BATCH_SIZE:
                upsert_batch(vectors)
                vectors = []

        if vectors:
            upsert_batch(vectors)

        print(f"    ✓ {source_name} done.")


if __name__ == "__main__":
    ingest_seed()
    ingest_books()

    stats = index.describe_index_stats()
    print(f"\n✅ Done. Pinecone index now has {stats.total_vector_count} vectors.")
