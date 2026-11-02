from .base import VectorStore


def build_store(settings) -> VectorStore:
    kind = settings.vector_store
    if kind == "memory":
        from .memory import MemoryStore

        return MemoryStore()
    if kind == "pgvector":
        from .pgvector import PgVectorStore

        return PgVectorStore(settings.database_url, settings.embed_dim)
    if kind == "qdrant":
        from .qdrant import QdrantStore

        return QdrantStore(settings.qdrant_url, settings.embed_dim)
    raise ValueError(f"Unknown vector_store: {kind}")
