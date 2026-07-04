import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from .base import VectorStore


class PgVectorStore(VectorStore):
    """Postgres + pgvector store. Raises on construction if the database
    or extension is unavailable — the factory catches that and falls back."""

    def __init__(self, database_url: str, dim: int) -> None:
        self._conn = psycopg.connect(database_url, autocommit=True)
        self._conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(self._conn)
        self._conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS vectors (
                namespace TEXT NOT NULL,
                id TEXT NOT NULL,
                embedding vector({dim}) NOT NULL,
                PRIMARY KEY (namespace, id)
            )
            """
        )

    def upsert(self, namespace: str, ids: list[str], vectors: np.ndarray) -> None:
        with self._conn.cursor() as cur:
            for id_, vec in zip(ids, vectors):
                cur.execute(
                    """
                    INSERT INTO vectors (namespace, id, embedding)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (namespace, id) DO UPDATE SET embedding = EXCLUDED.embedding
                    """,
                    (namespace, id_, np.asarray(vec, dtype=np.float32)),
                )

    def query(self, namespace: str, vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        rows = self._conn.execute(
            """
            SELECT id, 1 - (embedding <=> %s) AS similarity
            FROM vectors WHERE namespace = %s
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (np.asarray(vector, dtype=np.float32), namespace, np.asarray(vector, dtype=np.float32), top_k),
        ).fetchall()
        return [(r[0], float(r[1])) for r in rows]

    def count(self, namespace: str) -> int:
        row = self._conn.execute(
            "SELECT count(*) FROM vectors WHERE namespace = %s", (namespace,)
        ).fetchone()
        return int(row[0])
