"""Qdrant store. Tenant isolation via a payload filter on tenant_id.

Needs `qdrant-client`; set QDRANT_URL and VECTOR_STORE=qdrant.
"""
from __future__ import annotations

import numpy as np

from ..schemas import Chunk
from .base import VectorStore

COLLECTION = "rag_chunks"


class QdrantStore(VectorStore):
    def __init__(self, url: str, dim: int):
        if not url:
            raise RuntimeError("Qdrant store needs QDRANT_URL.")
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self._client = QdrantClient(url=url)
        self._dim = dim
        existing = {c.name for c in self._client.get_collections().collections}
        if COLLECTION not in existing:
            self._client.create_collection(
                COLLECTION, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(id=c.id, vector=list(map(float, v)),
                        payload={"tenant_id": c.tenant_id, "source": c.source,
                                 "chunk_index": c.chunk_index, "text": c.text})
            for c, v in zip(chunks, vectors)
        ]
        self._client.upsert(COLLECTION, points=points)

    def search(self, tenant_id: str, query_vec: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        flt = Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))])
        hits = self._client.search(COLLECTION, query_vector=list(map(float, query_vec)),
                                   query_filter=flt, limit=k)
        out = []
        for h in hits:
            p = h.payload
            out.append((Chunk(id=str(h.id), tenant_id=tenant_id, source=p["source"],
                              chunk_index=p["chunk_index"], text=p["text"]), float(h.score)))
        return out

    def _tenant_filter(self, tenant_id: str):
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        return Filter(must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))])

    def sources(self, tenant_id: str) -> list[tuple[str, int]]:
        from collections import Counter

        counts: Counter[str] = Counter()
        offset = None
        while True:
            points, offset = self._client.scroll(
                COLLECTION, scroll_filter=self._tenant_filter(tenant_id),
                limit=256, offset=offset, with_payload=True, with_vectors=False)
            counts.update(p.payload["source"] for p in points)
            if offset is None:
                break
        return sorted(counts.items())

    def clear(self, tenant_id: str) -> int:
        n = sum(c for _, c in self.sources(tenant_id))
        self._client.delete(COLLECTION, points_selector=self._tenant_filter(tenant_id))
        return n
