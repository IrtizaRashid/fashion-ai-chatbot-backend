import itertools

from models.product import ProductSearchRequest


DEFAULT_PRODUCT_TERMS = ["Shirt", "Oxford Shirt", "Polo Shirt", "Formal Shirt"]
DEFAULT_COLORS = ["Black", "Navy", "Blue", "White"]


class QueryGenerator:
    def generate(self, recommendations: ProductSearchRequest) -> list[str]:
        fits = [self._humanize(value) for value in recommendations.recommended_fit]
        products = [self._humanize(value) for value in recommendations.recommended_shirts] or DEFAULT_PRODUCT_TERMS
        colors = [self._humanize(value) for value in recommendations.recommended_colors] or DEFAULT_COLORS

        queries: list[str] = []

        for fit, color, product in itertools.product(fits or [""], colors, products):
            parts = [fit, color, product]
            queries.append(" ".join(part for part in parts if part))

        for color, product in itertools.product(colors, products):
            queries.append(f"{color} {product}")

        for fit, product in itertools.product(fits, products):
            queries.append(f"{fit} {product}")

        queries.extend(products)
        return self._dedupe(queries)[:16]

    @staticmethod
    def _humanize(value: str) -> str:
        return value.replace("_", " ").replace("-", " ").strip().title()

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for value in values:
            clean = " ".join(value.split())
            key = clean.lower()
            if clean and key not in seen:
                seen.add(key)
                output.append(clean)
        return output
