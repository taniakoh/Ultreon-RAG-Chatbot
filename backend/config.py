from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "sample-documents"
STORE_DIR = Path(__file__).resolve().parent / "vector_store"


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    LLM_MODEL: str = "anthropic/claude-3.5-sonnet"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 128
    SIMILARITY_TOP_K: int = 8
    USE_RERANKER: bool = True
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RERANK_TOP_N: int = 4
    USE_HYBRID_SEARCH: bool = True

    model_config = {"env_file": str(BASE_DIR / ".env"), "extra": "ignore"}


settings = Settings()
