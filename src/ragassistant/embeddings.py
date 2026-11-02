"""Embeddings behind one interface.

The default is a local, dependency-free hashing embedder so the whole system
runs with no API key: it maps text to a fixed-length L2-normalised vector via
hashed token n-grams. It is good enough to demonstrate real retrieval on the
sample corpus. For production quality, switch `EMBEDDER=openai`.
"""
from __future__ import annotations

import hashlib
import re

import numpy as np

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class LocalHashingEmbedder:
    name = "local"

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            toks = _tokens(t)
            for j in range(len(toks)):
                # unigram + bigram features, hashed into the vector
                for gram in (toks[j], " ".join(toks[j : j + 2])):
                    h = int(hashlib.md5(gram.encode()).hexdigest(), 16)
                    out[i, h % self.dim] += 1.0
            n = np.linalg.norm(out[i])
            if n:
                out[i] /= n
        return out


class OpenAIEmbedder:
    name = "openai"

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        if not api_key:
            raise RuntimeError("OpenAI embedder needs LLM_API_KEY.")
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def embed(self, texts: list[str]) -> np.ndarray:
        resp = self._client.embeddings.create(model=self._model, input=texts)
        return np.array([d.embedding for d in resp.data], dtype=np.float32)


def build_embedder(settings):
    if settings.embedder == "openai":
        return OpenAIEmbedder(settings.llm_api_key)
    return LocalHashingEmbedder(settings.embed_dim)
