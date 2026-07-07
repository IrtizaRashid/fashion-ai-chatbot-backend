"""Deterministic product ranking for the fashion recommendation engine."""

from __future__ import annotations

import re

from services.product_gender_filter import is_mens_product as product_is_mens
from recommendation.schemas import BodyAnalysis, ProductInput, Recommendation


class ProductRanker:
    """Scores men's products against body analysis and optional user constraints."""

    def rank(
        self,
        body_analysis: BodyAnalysis,
        products: list[ProductInput],
        budget: int | None = None,
        occasion: str | None = None,
        limit: int = 10,
    ) -> list[Recommendation]:
        recommendations = [
            self.score_product(body_analysis, product, budget, occasion)
            for product in products
            if self.is_mens_product(product)
        ]
        return sorted(recommendations, key=lambda item: item.match_score, reverse=True)[:limit]

    def score_product(
        self,
        body_analysis: BodyAnalysis,
        product: ProductInput,
        budget: int | None = None,
        occasion: str | None = None,
    ) -> Recommendation:
        score = 50
        strengths: list[str] = []
        weaknesses: list[str] = []

        product_text = self._product_text(product)
        recommended_fits = [item.lower() for item in body_analysis.recommended_fit]
        recommended_colors = [item.lower() for item in body_analysis.recommended_colors]
        recommended_patterns = [item.lower() for item in body_analysis.recommended_patterns]
        avoid_terms = [item.lower() for item in body_analysis.avoid]

        fit_score = self._fit_score(product_text, recommended_fits, avoid_terms)
        score += fit_score
        if fit_score >= 10:
            strengths.append("Strong fit match")
        elif fit_score < 0:
            weaknesses.append("Fit may not match the body profile")

        color_score = self._color_score(product, product_text, recommended_colors)
        score += color_score
        if color_score >= 10:
            strengths.append("Recommended color")
        elif recommended_colors:
            weaknesses.append("Color is not a top recommendation")

        pattern_score = self._pattern_score(product_text, recommended_patterns)
        score += pattern_score
        if pattern_score >= 6:
            strengths.append("Pattern suits the recommendation")

        material_score = self._material_score(product.material)
        score += material_score
        if material_score >= 6:
            strengths.append("Comfortable material")

        budget_score = self._budget_score(product.price, budget)
        score += budget_score
        if budget is not None:
            if budget_score >= 8:
                strengths.append("Within budget")
            elif budget_score < 0:
                weaknesses.append("Above budget")

        occasion_score = self._occasion_score(product_text, occasion)
        score += occasion_score
        if occasion_score >= 6 and occasion:
            strengths.append(f"Good for {occasion}")

        if product.available is False:
            score -= 25
            weaknesses.append("May be unavailable")

        score = max(0, min(100, round(score)))
        recommendation = self._level(score)
        reason = self._reason(body_analysis, product, strengths, weaknesses)

        return Recommendation(
            brand=product.brand,
            title=product.title,
            match_score=score,
            recommendation=recommendation,
            reason=reason,
            strengths=strengths[:4] or ["Reasonable style match"],
            weaknesses=weaknesses[:3],
            product_url=product.product_url,
            image_url=product.image_url,
            price=product.price,
            currency=product.currency,
            color=product.color,
            sizes=product.sizes,
            material=product.material,
        )

    @classmethod
    def is_mens_product(cls, product: ProductInput) -> bool:
        return product_is_mens(product)

    @staticmethod
    def _product_text(product: ProductInput) -> str:
        return " ".join(
            [
                product.title,
                product.brand,
                product.color or "",
                " ".join(product.colors),
                product.material or "",
                str(product.product_url or ""),
            ]
        ).lower().replace("-", " ")

    @staticmethod
    def _fit_score(product_text: str, recommended_fits: list[str], avoid_terms: list[str]) -> int:
        score = 0
        if any("slim" in fit for fit in recommended_fits) and "slim" in product_text:
            score += 18
        if any("regular" in fit for fit in recommended_fits) and "regular" in product_text:
            score += 14
        if any("straight" in fit for fit in recommended_fits) and ("straight" in product_text or "regular" in product_text):
            score += 12
        if any("oversized" in term for term in avoid_terms) and any(term in product_text for term in ["oversized", "boxy", "loose"]):
            score -= 16
        if any("tight" in term for term in avoid_terms) and "skinny" in product_text:
            score -= 14
        return score

    @staticmethod
    def _color_score(product: ProductInput, product_text: str, recommended_colors: list[str]) -> int:
        product_colors = {color.lower() for color in product.colors}
        if product.color:
            product_colors.add(product.color.lower())
        if any(color in product_colors or re.search(rf"\b{re.escape(color)}\b", product_text) for color in recommended_colors):
            return 16
        return 0

    @staticmethod
    def _pattern_score(product_text: str, recommended_patterns: list[str]) -> int:
        if not recommended_patterns:
            return 0
        if "solid" in recommended_patterns and not any(term in product_text for term in ["print", "graphic", "stripe", "check"]):
            return 8
        if any("stripe" in pattern for pattern in recommended_patterns) and "stripe" in product_text:
            return 8
        if any("check" in pattern for pattern in recommended_patterns) and "check" in product_text:
            return 7
        return 0

    @staticmethod
    def _material_score(material: str | None) -> int:
        if not material:
            return 0
        value = material.lower()
        if any(term in value for term in ["cotton", "linen", "denim", "twill"]):
            return 8
        if any(term in value for term in ["polyester", "fleece", "jersey"]):
            return 4
        return 0

    @staticmethod
    def _budget_score(price: int | None, budget: int | None) -> int:
        if budget is None or price is None:
            return 0
        if price <= budget:
            if price <= budget * 0.75:
                return 12
            return 8
        if price <= budget * 1.15:
            return -5
        return -18

    @staticmethod
    def _occasion_score(product_text: str, occasion: str | None) -> int:
        if not occasion:
            return 0
        value = occasion.lower()
        if any(term in value for term in ["office", "formal", "smart"]):
            if any(term in product_text for term in ["oxford", "button", "polo", "trouser", "chino"]):
                return 8
            if any(term in product_text for term in ["graphic", "activewear"]):
                return -8
        if any(term in value for term in ["casual", "daily", "college"]):
            if any(term in product_text for term in ["t shirt", "polo", "jean", "chino", "shirt"]):
                return 7
        if any(term in value for term in ["wedding", "party"]):
            if any(term in product_text for term in ["button", "oxford", "trouser"]):
                return 7
        return 0

    @staticmethod
    def _level(score: int) -> str:
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Good"
        if score >= 50:
            return "Fair"
        return "Poor"

    @staticmethod
    def _reason(
        body_analysis: BodyAnalysis,
        product: ProductInput,
        strengths: list[str],
        weaknesses: list[str],
    ) -> str:
        body = " ".join(
            part for part in [body_analysis.body_type, body_analysis.body_build] if part
        )
        main_strength = strengths[0].lower() if strengths else "a reasonable style match"
        if weaknesses:
            return (
                f"Based on the provided {body} analysis, this {product.title} is {main_strength}, "
                f"but {weaknesses[0].lower()}."
            )
        return (
            f"Based on the provided {body} analysis, this {product.title} is {main_strength} "
            "and should work well as a practical styling option."
        )

