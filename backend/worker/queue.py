"""RQ/Redis queue helpers."""

import os
from typing import Optional

from redis import Redis
from rq import Queue


REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
DEFAULT_QUEUE_NAME = os.getenv("RQ_QUEUE_NAME", "scheme_tasks")
_FAKE_REDIS_CONN = None


def get_redis_connection() -> Redis:
    if REDIS_URL.startswith("fakeredis://"):
        global _FAKE_REDIS_CONN
        import fakeredis  # lazy optional dependency
        if _FAKE_REDIS_CONN is None:
            _FAKE_REDIS_CONN = fakeredis.FakeRedis()
        return _FAKE_REDIS_CONN
    return Redis.from_url(REDIS_URL)


def get_queue(name: Optional[str] = None) -> Queue:
    redis_conn = get_redis_connection()
    return Queue(name or DEFAULT_QUEUE_NAME, connection=redis_conn)
