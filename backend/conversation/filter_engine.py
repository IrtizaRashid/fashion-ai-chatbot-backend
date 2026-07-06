"""Filters existing recommendations without scraping or searching websites."""

from __future__ import annotations

from conversation.schemas import FilterCriteria
from recommendation.schemas import Recommendation


class FilterEngine:
    def filter(self, recommendations: list[Recommendation], criteria: FilterCriteria) -> list[Recommendation]:
        filtered = list(recommendations)

        if criteria.brand:
            filtered = [item for item in filtered if self._match(item.brand, criteria.brand)]
        if criteria.exclude_brand:
            filtered = [item for item in filtered if not self._match(item.brand, criteria.exclude_brand)]
        if criteria.color:
            filtered = [item for item in filtered if self._contains(self._product_text(item), criteria.color)]
        if criteria.material:
            filtered = [item for item in filtered if self._contains(item.material or "", criteria.material)]
        if criteria.max_price is not None:
            filtered = [item for item in filtered if item.price is not None and item.price <= criteria.max_price]
        if criteria.min_price is not None:
            filtered = [item for item in filtered if item.price is not None and item.price >= criteria.min_price]
        if criteria.fit:
            filtered = [item for item in filtered if self._contains(self._product_text(item), criteria.fit)]
        if criteria.pattern:
            filtered = [item for item in filtered if self._contains(self._product_text(item), criteria.pattern)]
        if criteria.category:
            filtered = [item for item in filtered if self._category_match(item, criteria.category)]
        if criteria.available is not None:
            # Recommendation schema does not carry availability yet; keep all when unknown.
            filtered = filtered
        if criteria.occasion:
            filtered = [item for item in filtered if self._occasion_match(item, criteria.occasion)]

        if criteria.sort == "cheap":
            filtered = sorted(filtered, key=lambda item: item.price if item.price is not None else 10**9)
        elif criteria.sort == "expensive":
            filtered = sorted(filtered, key=lambda item: item.price if item.price is not None else -1, reverse=True)
        else:
            filtered = sorted(filtered, key=lambda item: item.match_score, reverse=True)

        return filtered

    @staticmethod
    def _product_text(item: Recommendation) -> str:
        return " ".join(
            [
                item.brand,
                item.title,
                item.color or "",
                item.material or "",
                " ".join(item.sizes),
                str(item.product_url or ""),
            ]
        ).lower().replace("-", " ")

    @staticmethod
    def _match(value: str | None, expected: str) -> bool:
        return bool(value and value.lower() == expected.lower())

    @staticmethod
    def _contains(value: str, expected: str) -> bool:
        return expected.lower().replace("-", " ") in value.lower().replace("-", " ")

    def _category_match(self, item: Recommendation, category: str) -> bool:
        text = self._product_text(item)
        value = category.lower()
        if "formal" in value:
            return any(term in text for term in ["formal", "oxford", "button", "dress shirt"])
        if "polo" in value:
            return "polo" in text
        if "t-shirt" in value or "tshirt" in value:
            return "t shirt" in text or "tshirt" in text or "tee" in text
        if "shirt" in value:
            return "shirt" in text
        if any(term in value for term in ["trouser", "pant", "jean", "chino"]):
            return any(term in text for term in ["trouser", "pant", "jean", "chino"])
        return self._contains(text, category)

    def _occasion_match(self, item: Recommendation, occasion: str) -> bool:
        text = self._product_text(item)
        value = occasion.lower()
        if "formal" in value:
            return any(term in text for term in ["formal", "oxford", "button", "polo", "trouser", "chino"])
        if "casual" in value:
            return any(term in text for term in ["t shirt", "tshirt", "polo", "jean", "chino", "shirt"])
        if "occasion" in value:
            return any(term in text for term in ["button", "oxford", "trouser", "shirt"])
        return True
