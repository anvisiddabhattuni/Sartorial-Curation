"""Event logging (board_submitted, results_rendered, card_clicked).

Writes to Postgres when available, otherwise appends JSONL to
backend/data/events.jsonl so instrumentation never blocks the pipeline.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("muse.events")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EVENTS_FILE = DATA_DIR / "events.jsonl"

_pg_conn = None


def init_events(database_url: str) -> None:
    """Try to set up the Postgres events table; fall back to JSONL silently."""
    global _pg_conn
    try:
        import psycopg

        _pg_conn = psycopg.connect(database_url, autocommit=True)
        _pg_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                properties JSONB NOT NULL DEFAULT '{}',
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        logger.info("Event logging: Postgres")
    except Exception as exc:  # pragma: no cover - environment dependent
        _pg_conn = None
        logger.warning("Event logging falling back to JSONL (%s)", exc)


def log_event(name: str, properties: dict[str, Any] | None = None) -> None:
    props = properties or {}
    if _pg_conn is not None:
        try:
            _pg_conn.execute(
                "INSERT INTO events (name, properties) VALUES (%s, %s)",
                (name, json.dumps(props)),
            )
            return
        except Exception as exc:
            logger.warning("Postgres event write failed, using JSONL (%s)", exc)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"name": name, "properties": props, "ts": time.time()}) + "\n")
