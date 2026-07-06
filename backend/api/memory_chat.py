"""Conversation chat endpoint using Redis-backed session memory."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from cache.cache_service import cache_service
from cache.redis_client import RedisSettings, RedisUnavailableError
from conversation.filter_engine import FilterEngine
from conversation.parser import FollowUpParser
from conversation.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationMessage,
    SessionCreateRequest,
    SessionResponse,
)
from recommendation.recommendation_engine import RecommendationEngine
from recommendation.schemas import BodyAnalysis, ProductInput, Recommendation, RecommendationRequest

logger = logging.getLogger(__name__)
router = APIRouter()

parser = FollowUpParser()
filter_engine = FilterEngine()
recommendation_engine = RecommendationEngine()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    try:
        payload = await cache_service.create_session(
            session_id=request.session_id,
            body_analysis=jsonable_encoder(request.body_analysis) if request.body_analysis else None,
            recommendations=jsonable_encoder(request.recommendations),
        )
        return _session_response(request.session_id, payload)
    except RedisUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Redis cache is unavailable") from exc


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    try:
        payload = await cache_service.get_session(session_id)
        return _session_response(session_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found or expired") from exc
    except RedisUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Redis cache is unavailable") from exc


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    try:
        await cache_service.delete_session(session_id)
        return {"status": "deleted", "session_id": session_id}
    except RedisUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Redis cache is unavailable") from exc


@router.post("/chat", response_model=ChatResponse)
async def memory_chat(request: ChatRequest) -> ChatResponse:
    try:
        payload = await _load_or_create_payload(request)
    except RedisUnavailableError as exc:
        logger.error("Redis unavailable during /chat: %s", exc)
        raise HTTPException(status_code=503, detail="Redis cache is unavailable. Please start Redis and try again.") from exc

    body_analysis = _body_analysis(payload)
    recommendations = _recommendations(payload.get("recommendations") or [])
    current_filtered = _recommendations(payload.get("current_filtered_recommendations") or []) or recommendations
    conversation = payload.get("conversation") or []
    conversation.append(_message("user", request.message))

    if not recommendations:
        reply = (
            "I do not have cached products for this session yet. Analyze the user, "
            "search products once, rank them, and cache those recommendations first."
        )
        conversation.append(_message("assistant", reply))
        await cache_service.update_session(request.session_id, {"conversation": conversation})
        return ChatResponse(reply=reply, recommendations=[], session_id=request.session_id)

    criteria = await parser.parse(request.message)
    source = recommendations if criteria.reset_filters else current_filtered
    filtered = filter_engine.filter(source, criteria)

    if not filtered:
        reply = "I could not find matching products in the cached list. Try clearing filters or using a broader request."
        conversation.append(_message("assistant", reply))
        await cache_service.update_session(
            request.session_id,
            {
                "conversation": conversation,
                "current_filtered_recommendations": [],
                "preferences": _updated_preferences(payload, criteria),
            },
        )
        return ChatResponse(reply=reply, recommendations=[], filters=criteria, session_id=request.session_id)

    ranked = filtered[:10]
    if body_analysis is not None:
        rank_request = RecommendationRequest(
            body_analysis=body_analysis,
            products=[
                ProductInput(
                    brand=item.brand,
                    title=item.title,
                    price=item.price,
                    currency=item.currency,
                    color=item.color,
                    material=item.material,
                    sizes=item.sizes,
                    product_url=item.product_url,
                    image_url=item.image_url,
                )
                for item in filtered
            ],
            budget=criteria.max_price,
            occasion=criteria.occasion,
        )
        ranked = (await recommendation_engine.recommend(rank_request)).recommendations

    reply = _build_reply(len(ranked), criteria)
    conversation.append(_message("assistant", reply))
    await cache_service.update_session(
        request.session_id,
        {
            "conversation": conversation,
            "current_filtered_recommendations": jsonable_encoder(ranked),
            "preferences": _updated_preferences(payload, criteria),
        },
    )

    return ChatResponse(
        reply=reply,
        recommendations=ranked,
        filters=criteria,
        session_id=request.session_id,
    )


async def _load_or_create_payload(request: ChatRequest) -> dict:
    recommendations = jsonable_encoder(request.recommendations) if request.recommendations is not None else None
    body_analysis = jsonable_encoder(request.body_analysis) if request.body_analysis else None

    if body_analysis is not None or recommendations is not None:
        return await cache_service.create_session(
            session_id=request.session_id,
            body_analysis=body_analysis,
            recommendations=recommendations,
        )

    return await cache_service.get_session(request.session_id)


def _session_response(session_id: str, payload: dict) -> SessionResponse:
    return SessionResponse(
        session_id=session_id,
        body_analysis=_body_analysis(payload),
        preferences=payload.get("preferences") or {},
        conversation_history=[
            ConversationMessage.model_validate(item)
            for item in payload.get("conversation", [])
        ],
        current_recommendations=_recommendations(payload.get("recommendations") or []),
        current_filtered_recommendations=_recommendations(payload.get("current_filtered_recommendations") or []),
        expires_at=datetime.utcnow() + timedelta(seconds=RedisSettings.SESSION_TTL_SECONDS),
    )


def _body_analysis(payload: dict) -> BodyAnalysis | None:
    value = payload.get("body_analysis")
    return BodyAnalysis.model_validate(value) if value else None


def _recommendations(items: list[dict]) -> list[Recommendation]:
    return [Recommendation.model_validate(item) for item in items]


def _message(role: str, content: str) -> dict:
    return {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
    }


def _updated_preferences(payload: dict, criteria) -> dict:
    preferences = dict(payload.get("preferences") or {})
    for key, value in criteria.model_dump().items():
        if value not in (None, False):
            preferences[key] = value
    return preferences


def _build_reply(count: int, criteria) -> str:
    parts: list[str] = []
    if criteria.color:
        parts.append(criteria.color)
    if criteria.material:
        parts.append(criteria.material)
    if criteria.category:
        parts.append(criteria.category)
    if criteria.brand:
        parts.append(criteria.brand)
    if criteria.exclude_brand:
        parts.append(f"excluding {criteria.exclude_brand}")
    if criteria.max_price is not None:
        parts.append(f"under PKR {criteria.max_price}")
    if criteria.min_price is not None:
        parts.append(f"above PKR {criteria.min_price}")
    if criteria.occasion:
        parts.append(criteria.occasion.lower())

    description = " ".join(parts) if parts else "matching"
    return f"I found {count} {description} option{'s' if count != 1 else ''} from the Redis-cached products and re-ranked them for your body profile."
