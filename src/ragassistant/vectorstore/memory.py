"""In-memory vector store. Default, so the system runs with no external database.

Vectors are kept per tenant, so a query physically cannot reach another tenant's
data. Fine for demos, tests and small corpora; use the pgvector or Qdrant store
for anything real.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from ..schemas import Chunk
from .base import VectorStore


class MemoryStore(VectorStore):
    def __init__(self):
        self._chunks: dict[str, list[Chunk]] = defaultdict(list)
        self._vecs: dict[str, list[np.ndarray]] = defaultdict(list)

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        for c, v in zip(chunks, vectors):
            self._chunks[c.tenant_id].append(c)
            self._vecs[c.tenant_id].append(v.astype(np.float32))

    def search(self, tenant_id: str, query_vec: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        vecs = self._vecs.get(tenant_id)
        if not vecs:
            return []
        M = np.vstack(vecs)
        q = query_vec / max(np.linalg.norm(query_vec), 1e-9)
        sims = M @ q
        order = np.argsort(sims)[::-1][:k]
        chunks = self._chunks[tenant_id]
        return [(chunks[i], float(sims[i])) for i in order]
