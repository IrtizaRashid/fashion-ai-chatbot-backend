"""Recommendation API endpoint."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from recommendation.recommendation_engine import RecommendationEngine
from recommendation.schemas import RecommendationRequest, RecommendationResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def get_recommendation_engine() -> RecommendationEngine:
    return RecommendationEngine()


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_products(request: RecommendationRequest) -> RecommendationResponse:
    """Rank already-scraped products against a body analysis."""
    if not request.products:
        raise HTTPException(status_code=400, detail="Products list cannot be empty")

    try:
        response = await get_recommendation_engine().recommend(request)
    except ValidationError as exc:
        logger.warning("Invalid recommendation request: %s", exc)
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Recommendation engine failed")
        raise HTTPException(status_code=500, detail=f"Recommendation engine failed: {exc}") from exc

    if not response.recommendations:
        raise HTTPException(status_code=404, detail="No suitable recommendations found")

    return response
