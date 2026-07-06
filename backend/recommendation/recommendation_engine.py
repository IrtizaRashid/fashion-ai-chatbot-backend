"""Recommendation engine orchestration."""

from __future__ import annotations

import logging

from recommendation.gemini_recommender import GeminiRecommendationError, GeminiRecommender
from recommendation.product_ranker import ProductRanker
from recommendation.schemas import RecommendationRequest, RecommendationResponse

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Ranks scraped products and returns the best recommendations."""

    def __init__(
        self,
        ranker: ProductRanker | None = None,
        gemini_recommender: GeminiRecommender | None = None,
    ) -> None:
        self.ranker = ranker or ProductRanker()
        self.gemini_recommender = gemini_recommender or GeminiRecommender()

    async def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        if not request.products:
            raise ValueError("At least one product is required")

        filtered_products = [
            product for product in request.products if self.ranker.is_mens_product(product)
        ]
        if not filtered_products:
            return RecommendationResponse(recommendations=[])

        men_only_request = request.model_copy(update={"products": filtered_products})

        # First produce deterministic scores so the endpoint remains reliable.
        fallback_recommendations = self.ranker.rank(
            body_analysis=request.body_analysis,
            products=filtered_products,
            budget=request.budget,
            occasion=request.occasion,
            limit=10,
        )

        try:
            gemini_recommendations = await self.gemini_recommender.recommend(men_only_request)
            if gemini_recommendations:
                return RecommendationResponse(recommendations=gemini_recommendations[:10])
        except GeminiRecommendationError as exc:
            logger.warning("Using deterministic recommendation fallback: %s", exc)

        return RecommendationResponse(recommendations=fallback_recommendations[:10])
