"""Redis-backed session cache."""

from __future__ import annotations

import json
import logging
import zlib
from base64 import b64decode, b64encode
from datetime import datetime
from typing import Any

from cache.redis_client import RedisSettings, RedisUnavailableError, get_redis_client

logger = logging.getLogger(__name__)


class SessionCache:
    """Stores temporary fashion chat sessions in Redis."""

    def __init__(self, ttl_seconds: int | None = None) -> None:
        self.ttl_seconds = ttl_seconds or RedisSettings.SESSION_TTL_SECONDS
        self.redis = get_redis_client()

    async def create_session(
        self,
        session_id: str,
        body_analysis: dict[str, Any] | None = None,
        products: list[dict[str, Any]] | None = None,
        recommendations: list[dict[str, Any]] | None = None,
        preferences: dict[str, Any] | None = None,
        conversation: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        now = self._now()
        existing = await self.get_session(session_id, raise_missing=False)
        payload = existing or {
            "conversation": [],
            "body_analysis": None,
            "products": [],
            "recommendations": [],
            "current_filtered_recommendations": [],
            "preferences": {},
            "created_at": now,
            "updated_at": now,
        }

        if body_analysis is not None:
            payload["body_analysis"] = body_analysis
        if products is not None:
            payload["products"] = products
        if recommendations is not None:
            payload["recommendations"] = recommendations
            payload["current_filtered_recommendations"] = recommendations
        if preferences is not None:
            payload["preferences"] = {**payload.get("preferences", {}), **preferences}
        if conversation is not None:
            payload["conversation"] = conversation

        payload["updated_at"] = now
        await self._set(session_id, payload)
        logger.info("Redis session created/updated: %s", session_id)
        return payload

    async def get_session(self, session_id: str, raise_missing: bool = True) -> dict[str, Any] | None:
        key = self._key(session_id)
        try:
            raw = await self.redis.get(key)
        except Exception as exc:
            logger.error("Redis get failed for %s: %s", key, exc)
            raise RedisUnavailableError("Redis is unavailable") from exc

        if raw is None:
            logger.info("Redis cache miss: %s", key)
            if raise_missing:
                raise KeyError(session_id)
            return None

        logger.info("Redis cache hit: %s", key)
        await self.refresh_session(session_id)
        return self._decode(raw)

    async def update_session(self, session_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        payload = await self.get_session(session_id)
        payload.update(updates)
        payload["updated_at"] = self._now()
        await self._set(session_id, payload)
        logger.info("Redis session updated: %s", session_id)
        return payload

    async def delete_session(self, session_id: str) -> None:
        try:
            await self.redis.delete(self._key(session_id))
            logger.info("Redis session deleted: %s", session_id)
        except Exception as exc:
            logger.error("Redis delete failed for %s: %s", session_id, exc)
            raise RedisUnavailableError("Redis is unavailable") from exc

    async def refresh_session(self, session_id: str) -> None:
        try:
            await self.redis.expire(self._key(session_id), self.ttl_seconds)
        except Exception as exc:
            logger.error("Redis expire failed for %s: %s", session_id, exc)
            raise RedisUnavailableError("Redis is unavailable") from exc

    async def cache_products(self, session_id: str, products: list[dict[str, Any]]) -> dict[str, Any]:
        return await self.update_session(session_id, {"products": products})

    async def cache_body_analysis(self, session_id: str, body_analysis: dict[str, Any]) -> dict[str, Any]:
        return await self.update_session(session_id, {"body_analysis": body_analysis})

    async def cache_recommendations(self, session_id: str, recommendations: list[dict[str, Any]]) -> dict[str, Any]:
        return await self.update_session(
            session_id,
            {
                "recommendations": recommendations,
                "current_filtered_recommendations": recommendations,
            },
        )

    async def _set(self, session_id: str, payload: dict[str, Any]) -> None:
        key = self._key(session_id)
        encoded = self._encode(payload)
        try:
            await self.redis.set(key, encoded, ex=self.ttl_seconds)
        except Exception as exc:
            logger.error("Redis set failed for %s: %s", key, exc)
            raise RedisUnavailableError("Redis is unavailable") from exc

    @staticmethod
    def _key(session_id: str) -> str:
        return f"session:{session_id}"

    @staticmethod
    def _now() -> str:
        return datetime.utcnow().isoformat()

    @staticmethod
    def _encode(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        # Compress larger session payloads, especially product lists.
        if len(raw) > 4096:
            return "z:" + b64encode(zlib.compress(raw)).decode("ascii")
        return "j:" + raw.decode("utf-8")

    @staticmethod
    def _decode(raw: str) -> dict[str, Any]:
        if raw.startswith("z:"):
            return json.loads(zlib.decompress(b64decode(raw[2:])).decode("utf-8"))
        if raw.startswith("j:"):
            return json.loads(raw[2:])
        return json.loads(raw)
