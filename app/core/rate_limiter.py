import time
from collections import deque
from threading import Lock


class SimpleRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = deque()
                self._buckets[key] = bucket

            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= limit:
                return False

            bucket.append(now)
            return True


_limiter = SimpleRateLimiter()


def rate_limit(*, key: str, limit: int, window_seconds: int) -> None:
    from fastapi import HTTPException

    if not _limiter.allow(key, limit, window_seconds):
        raise HTTPException(status_code=429, detail="Too many requests")
