"""Gemini recommender for richer product ranking explanations."""

from __future__ import annotations

import json
import logging
from typing import Any

import google.generativeai as genai

from core.config import settings
from recommendation.prompts import RECOMMENDATION_JSON_INSTRUCTIONS, RECOMMENDER_SYSTEM_PROMPT
from recommendation.schemas import Recommendation, RecommendationRequest

logger = logging.getLogger(__name__)


class GeminiRecommendationError(RuntimeError):
    """Raised when Gemini cannot produce valid recommendation JSON."""


class GeminiRecommender:
    """Calls Gemini 2.5 Flash to rank products with stylist reasoning."""

    async def recommend(self, request: RecommendationRequest) -> list[Recommendation]:
        if not settings.GEMINI_API_KEY:
            raise GeminiRecommendationError("GEMINI_API_KEY is not configured")

        prompt = self._build_prompt(request)
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
            payload = self._parse_json(text)
            items = payload.get("recommendations", [])
            if not isinstance(items, list) or not items:
                raise GeminiRecommendationError("Gemini returned no recommendations")

            recommendations = [Recommendation.model_validate(item) for item in items]
            return sorted(recommendations, key=lambda item: item.match_score, reverse=True)[:10]
        except GeminiRecommendationError:
            raise
        except Exception as exc:
            logger.warning("Gemini recommendation failed: %s", exc)
            raise GeminiRecommendationError(str(exc)) from exc

    @staticmethod
    def _build_prompt(request: RecommendationRequest) -> str:
        body = request.body_analysis.model_dump()
        products = [product.model_dump(mode="json") for product in request.products]
        return f"""
{RECOMMENDER_SYSTEM_PROMPT}

{RECOMMENDATION_JSON_INSTRUCTIONS}

Budget:
{request.budget}

Occasion:
{request.occasion}

Body analysis:
{json.dumps(body, ensure_ascii=False)}

Products:
{json.dumps(products, ensure_ascii=False)}

Return this JSON shape only:
{{
  "recommendations": [
    {{
      "brand": "...",
      "title": "...",
      "match_score": 0,
      "recommendation": "Excellent",
      "reason": "...",
      "strengths": ["..."],
      "weaknesses": ["..."],
      "product_url": "...",
      "image_url": "...",
      "price": 0,
      "currency": "PKR",
      "color": "...",
      "sizes": ["..."],
      "material": "..."
    }}
  ]
}}
"""

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.strip("`")
            if clean.lower().startswith("json"):
                clean = clean[4:].strip()
        start = clean.find("{")
        end = clean.rfind("}")
        if start == -1 or end == -1:
            raise GeminiRecommendationError("Gemini response did not contain JSON")
        return json.loads(clean[start : end + 1])
