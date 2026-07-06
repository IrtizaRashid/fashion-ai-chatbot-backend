import re
from urllib.parse import urljoin, urlparse

from models.product import Product


PRICE_PATTERN = re.compile(r"(?:PKR|Rs\.?|â‚¨)?\s*([0-9][0-9,]*)", re.IGNORECASE)
SIZE_PATTERN = re.compile(r"\b(XS|S|M|L|XL|XXL|2XL|3XL|30|32|34|36|38|40)\b", re.IGNORECASE)

MATERIALS = ["cotton", "linen", "denim", "polyester", "fleece", "viscose", "wool", "twill", "jersey"]
COLORS = [
    "black",
    "white",
    "blue",
    "navy",
    "green",
    "red",
    "brown",
    "grey",
    "gray",
    "beige",
    "maroon",
    "olive",
    "khaki",
    "cream",
    "pink",
    "purple",
    "yellow",
]


class ProductNormalizer:
    def normalize_price(self, text: str | None) -> int | None:
        if not text:
            return None

        prices: list[int] = []
        for match in PRICE_PATTERN.finditer(text):
            end = match.end()
            if end < len(text) and text[end : end + 1] == "%":
                continue
            try:
                value = int(match.group(1).replace(",", ""))
            except ValueError:
                continue
            if value >= 100:
                prices.append(value)

        return min(prices) if prices else None

    def extract_colors(self, title: str, text: str = "", product_url: str | None = None) -> list[str]:
        colors: list[str] = []
        url_color = self._color_from_url(product_url)
        if url_color:
            colors.append(url_color)

        searchable = f"{title} {text}".lower()
        for color in COLORS:
            if color in searchable:
                normalized = "Grey" if color == "gray" else color.title()
                if normalized not in colors:
                    colors.append(normalized)
        return colors

    def extract_material(self, text: str) -> str | None:
        lowered = text.lower()
        for material in MATERIALS:
            if material in lowered:
                return material.title()
        return None

    def extract_sizes(self, text: str) -> list[str]:
        sizes = {match.group(1).upper() for match in SIZE_PATTERN.finditer(text)}
        return sorted(sizes)

    def absolute_url(self, base_url: str, url: str | None) -> str | None:
        if not url:
            return None
        if url.startswith("//"):
            return f"https:{url}"
        return urljoin(base_url, url)

    def is_product_url(self, url: str | None) -> bool:
        if not url:
            return False

        parsed = urlparse(url)
        path = parsed.path.lower()
        if not path or path == "/":
            return False

        blocked_parts = [
            "/search",
            "/collections",
            "/collection",
            "/categories",
            "/category",
            "/pages",
            "/blogs",
            "/account",
            "/cart",
        ]
        if any(part in path for part in blocked_parts):
            return False

        return "/products/" in path or path.endswith(".html") or len(path.strip("/").split("/")) >= 1

    def dedupe(self, products: list[Product]) -> list[Product]:
        seen: set[str] = set()
        deduped: list[Product] = []

        for product in products:
            key = str(product.product_url or product.title).split("?")[0].strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(product)
        return deduped

    def _color_from_url(self, product_url: str | None) -> str | None:
        if not product_url:
            return None

        lowered = product_url.lower()
        code_map = {
            "blk": "Black",
            "wht": "White",
            "nvy": "Navy",
            "blu": "Blue",
            "grn": "Green",
            "gry": "Grey",
            "red": "Red",
            "brn": "Brown",
            "olv": "Olive",
            "kha": "Khaki",
        }
        for code, color in code_map.items():
            if f"-{code}" in lowered or f"_{code}" in lowered:
                return color
        return None
