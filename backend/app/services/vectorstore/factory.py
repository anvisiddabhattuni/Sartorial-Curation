import logging
from functools import lru_cache

from ...config import get_settings
from .base import VectorStore
from .memory import InMemoryVectorStore

logger = logging.getLogger("muse.vectorstore")


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    if settings.vector_store == "pgvector":
        try:
            from .pg import PgVectorStore

            store = PgVectorStore(settings.database_url, settings.embedding_dim)
            logger.info("Vector store: pgvector (%s)", settings.database_url)
            return store
        except Exception as exc:
            logger.warning("pgvector unavailable (%s) — falling back to in-memory store", exc)
    logger.info("Vector store: in-memory")
    return InMemoryVectorStore()
