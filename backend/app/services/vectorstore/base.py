from abc import ABC, abstractmethod

import numpy as np


class VectorStore(ABC):
    """Stores product vectors and answers nearest-neighbour queries.

    Implementations: PgVectorStore (Postgres + pgvector) and
    InMemoryVectorStore (numpy cosine similarity fallback).
    """

    @abstractmethod
    def upsert(self, namespace: str, ids: list[str], vectors: np.ndarray) -> None:
        """Insert or replace vectors for the given ids within a namespace."""

    @abstractmethod
    def query(self, namespace: str, vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        """Return (id, cosine_similarity) pairs, best first."""

    @abstractmethod
    def count(self, namespace: str) -> int:
        """Number of vectors stored in a namespace."""
