"""PostgreSQL + pgvector store.

Tenant isolation is enforced in the WHERE clause, so a query for one tenant can
never scan another's rows. Needs `psycopg[binary]` and a Postgres with the
`vector` extension; set DATABASE_URL and VECTOR_STORE=pgvector.

The schema and queries are standard; the production hardening (row-level
security policies, connection pooling, and the index tuning for large corpora)
is reserved, see README.
"""
from __future__ import annotations

import numpy as np

from ..schemas import Chunk
from .base import VectorStore


class PgVectorStore(VectorStore):
    def __init__(self, dsn: str, dim: int):
        if not dsn:
            raise RuntimeError("pgvector store needs DATABASE_URL.")
        import psycopg  # noqa: F401

        self._dsn = dsn
        self._dim = dim
        self._init_schema()

    def _conn(self):
        import psycopg

        return psycopg.connect(self._dsn)

    def _init_schema(self):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    chunk_index INT NOT NULL,
                    text TEXT NOT NULL,
                    embedding vector({self._dim})
                )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS chunks_tenant_idx ON chunks (tenant_id)")
            conn.commit()

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        with self._conn() as conn, conn.cursor() as cur:
            for c, v in zip(chunks, vectors):
                cur.execute(
                    "INSERT INTO chunks (id, tenant_id, source, chunk_index, text, embedding) "
                    "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
                    (c.id, c.tenant_id, c.source, c.chunk_index, c.text, list(map(float, v))),
                )
            conn.commit()

    def search(self, tenant_id: str, query_vec: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        q = list(map(float, query_vec))
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT id, source, chunk_index, text, 1 - (embedding <=> %s::vector) AS score "
                "FROM chunks WHERE tenant_id = %s "
                "ORDER BY embedding <=> %s::vector LIMIT %s",
                (q, tenant_id, q, k),
            )
            rows = cur.fetchall()
        out = []
        for rid, source, idx, text, score in rows:
            out.append((Chunk(id=rid, tenant_id=tenant_id, source=source,
                              chunk_index=idx, text=text), float(score)))
        return out
