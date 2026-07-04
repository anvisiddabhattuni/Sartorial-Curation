import numpy as np

from .base import VectorStore


class InMemoryVectorStore(VectorStore):
    """Numpy cosine-similarity store. Fallback when Postgres is unavailable;
    plenty fast at catalog scale (<10k vectors)."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, np.ndarray]] = {}

    def upsert(self, namespace: str, ids: list[str], vectors: np.ndarray) -> None:
        ns = self._data.setdefault(namespace, {})
        for id_, vec in zip(ids, vectors):
            ns[id_] = np.asarray(vec, dtype=np.float32)

    def query(self, namespace: str, vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        ns = self._data.get(namespace, {})
        if not ns:
            return []
        ids = list(ns.keys())
        mat = np.stack([ns[i] for i in ids])
        q = np.asarray(vector, dtype=np.float32)
        sims = (mat @ q) / (np.linalg.norm(mat, axis=1) * np.linalg.norm(q) + 1e-9)
        order = np.argsort(-sims)[:top_k]
        return [(ids[i], float(sims[i])) for i in order]

    def count(self, namespace: str) -> int:
        return len(self._data.get(namespace, {}))
