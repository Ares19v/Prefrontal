from sentence_transformers import SentenceTransformer
import threading

_lock = threading.Lock()
_instance = None


def get_embedder() -> "BGEEmbedder":
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = BGEEmbedder()
    return _instance


class BGEEmbedder:
    """
    Wrapper around BAAI/bge-base-en-v1.5 (768-dim, cosine).
    Uses a query prefix for better retrieval quality per BGE recommendations.
    """

    QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

    def __init__(self):
        print("Loading BAAI/bge-base-en-v1.5 — first run downloads ~440 MB...")
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        print("Embedding model ready.")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of document chunks for indexing."""
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Embed a single user query (with BGE query prefix)."""
        vector = self.model.encode(
            self.QUERY_PREFIX + text,
            normalize_embeddings=True,
        )
        return vector.tolist()

    @property
    def dimension(self) -> int:
        return 768
