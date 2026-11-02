from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from ..schemas import Chunk


class VectorStore(ABC):
    """Every store enforces tenant isolation at query time: a search for tenant A
    can never return tenant B's chunks. This is the first line of the multi-tenant
    guarantee (see also security.py)."""

    @abstractmethod
    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None: ...

    @abstractmethod
    def search(self, tenant_id: str, query_vec: np.ndarray, k: int) -> list[tuple[Chunk, float]]: ...

    @abstractmethod
    def sources(self, tenant_id: str) -> list[tuple[str, int]]:
        """What this tenant has indexed, as (source, chunk count). Scoped the same
        way a search is, so it cannot report another tenant's documents."""

    @abstractmethod
    def clear(self, tenant_id: str) -> int:
        """Remove everything belonging to this tenant, and return how many chunks
        went. Also the honest answer to "can you delete a customer's data"."""
