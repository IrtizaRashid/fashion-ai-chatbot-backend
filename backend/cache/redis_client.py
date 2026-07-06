"""Redis client setup for async cache access."""

from __future__ import annotations

import logging
import os
from functools import lru_cache

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisUnavailableError(RuntimeError):
    """Raised when Redis cannot be reached."""


class RedisSettings:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SESSION_TTL_SECONDS: int = int(os.getenv("SESSION_TTL_SECONDS", "1800"))
    REDIS_SOCKET_TIMEOUT: float = float(os.getenv("REDIS_SOCKET_TIMEOUT", "3"))


@lru_cache
def get_redis_client() -> redis.Redis:
    return redis.from_url(
        RedisSettings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_timeout=RedisSettings.REDIS_SOCKET_TIMEOUT,
        socket_connect_timeout=RedisSettings.REDIS_SOCKET_TIMEOUT,
    )


async def ping_redis() -> bool:
    try:
        await get_redis_client().ping()
        return True
    except Exception as exc:
        logger.error("Redis ping failed: %s", exc)
        return False
