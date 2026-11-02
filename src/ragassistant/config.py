from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # mock | openai | anthropic | gemini
    llm_provider: str = "mock"
    llm_model: str = ""
    llm_api_key: str = ""

    # local | openai
    embedder: str = "local"
    embed_dim: int = 256

    # memory | pgvector | qdrant
    vector_store: str = "memory"
    database_url: str = ""          # for pgvector
    qdrant_url: str = ""            # for qdrant

    chunk_size: int = 500
    chunk_overlap: int = 80
    top_k: int = 5
    # Fraction of the question's content words that must appear in the retrieved
    # context to answer; below this the graph escalates to a human.
    min_confidence: float = 0.34

    system_prompt: str = (
        "You answer only from the provided context and always cite sources as [n]. "
        "If the context does not contain the answer, say you don't know."
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
