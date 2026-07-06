"""High-level cache service used by API endpoints."""

from __future__ import annotations

from typing import Any

from cache.session_cache import SessionCache


class CacheService:
    def __init__(self, session_cache: SessionCache | None = None) -> None:
        self.session_cache = session_cache or SessionCache()

    async def create_session(
        self,
        session_id: str,
        body_analysis: dict[str, Any] | None = None,
        products: list[dict[str, Any]] | None = None,
        recommendations: list[dict[str, Any]] | None = None,
        preferences: dict[str, Any] | None = None,
        conversation: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return await self.session_cache.create_session(
            session_id=session_id,
            body_analysis=body_analysis,
            products=products,
            recommendations=recommendations,
            preferences=preferences,
            conversation=conversation,
        )

    async def get_session(self, session_id: str) -> dict[str, Any]:
        return await self.session_cache.get_session(session_id)

    async def update_session(self, session_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        return await self.session_cache.update_session(session_id, updates)

    async def delete_session(self, session_id: str) -> None:
        await self.session_cache.delete_session(session_id)

    async def refresh_session(self, session_id: str) -> None:
        await self.session_cache.refresh_session(session_id)

    async def cache_products(self, session_id: str, products: list[dict[str, Any]]) -> dict[str, Any]:
        return await self.session_cache.cache_products(session_id, products)

    async def cache_body_analysis(self, session_id: str, body_analysis: dict[str, Any]) -> dict[str, Any]:
        return await self.session_cache.cache_body_analysis(session_id, body_analysis)

    async def cache_recommendations(self, session_id: str, recommendations: list[dict[str, Any]]) -> dict[str, Any]:
        return await self.session_cache.cache_recommendations(session_id, recommendations)


cache_service = CacheService()
