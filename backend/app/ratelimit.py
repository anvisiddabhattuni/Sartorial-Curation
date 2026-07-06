"""In-memory per-IP rate limiting. Deliberately simple: a single Railway
instance, no shared state needed across processes. Resets on restart, which
is fine — the goal is smoothing out a traffic spike, not perfect accounting."""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            dq = self._hits[key]
            while dq and now - dq[0] > self.window_seconds:
                dq.popleft()
            if len(dq) >= self.max_requests:
                return False
            dq.append(now)
            return True


def client_ip(request: Request) -> str:
    # Railway (and most PaaS) terminate TLS and proxy to the container, so
    # request.client.host is the proxy's address, not the visitor's. Trust
    # the first hop of X-Forwarded-For instead when present.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit_dependency(limiter: RateLimiter, action: str):
    async def _check(request: Request) -> None:
        if not limiter.allow(client_ip(request)):
            raise HTTPException(
                status_code=429,
                detail=f"Too many {action} requests — please wait a bit and try again.",
            )

    return _check
