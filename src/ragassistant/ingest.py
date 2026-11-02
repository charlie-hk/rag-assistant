"""Document ingestion: load, chunk, and prepare for embedding.

Text comes in directly or from a PDF (via pypdf). Chunking is character-based
with overlap, which keeps related sentences together and gives the retriever
enough context per chunk.
"""
from __future__ import annotations

import hashlib

from .schemas import Chunk


def load_pdf(path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(path)
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def make_chunks(tenant_id: str, source: str, text: str, size: int, overlap: int) -> list[Chunk]:
    out = []
    for i, piece in enumerate(chunk_text(text, size, overlap)):
        cid = hashlib.md5(f"{tenant_id}:{source}:{i}".encode()).hexdigest()[:16]
        out.append(Chunk(id=cid, tenant_id=tenant_id, source=source, chunk_index=i, text=piece))
    return out
