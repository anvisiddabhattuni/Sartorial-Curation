"""Daily ceilings on calls to metered third-party APIs (Gemini, SerpAPI).

Unlike the rate limiter (which protects against one client hammering the
API), this protects the whole deployment against a traffic spike quietly
burning through paid/rate-limited quota. When a budget is exhausted, callers
should fall back to the free stub/mock equivalent rather than error —
consistent with the rest of the pipeline's fallback-first design.
"""

import logging
import threading
from datetime import date, datetime, timezone

logger = logging.getLogger("muse.budget")


class DailyBudget:
    def __init__(self, name: str, limit: int) -> None:
        self.name = name
        self.limit = limit
        self._lock = threading.Lock()
        self._day = self._today()
        self._count = 0

    @staticmethod
    def _today() -> date:
        return datetime.now(timezone.utc).date()

    def try_consume(self) -> bool:
        if self.limit <= 0:
            return True  # 0 or negative = unlimited (opt out)
        with self._lock:
            today = self._today()
            if today != self._day:
                self._day = today
                self._count = 0
            if self._count >= self.limit:
                logger.warning("%s daily budget exhausted (%d/%d)", self.name, self._count, self.limit)
                return False
            self._count += 1
            return True
