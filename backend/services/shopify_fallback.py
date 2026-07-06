import json
import re
import ssl
from urllib.request import Request, urlopen

from models.product import Product
from services.product_normalizer import ProductNormalizer


class ShopifyFallbackClient:
    """Fallback product extractor for Shopify stores when rendered cards are blocked or changed."""

    BOYS_BLOCKED_TERMS = [
        "girl",
        "girls",
        "women",
        "woman",
        "ladies",
        "female",
        "cropped",
        "crop",
        "lace",
        "skirt",
        "dress",
        "blouse",
        "camisole",
        "bra",
        "bralette",
        "tights",
        "legging",
        "leggings",
        "frock",
        "kurti",
        "dupatta",
        "heels",
        "makeup",
        "kids girls",
        "baby girl",
        "super cropped",
        "with lace",
        "lace detail",
        "/women",
        "/girls",
        "/ladies",
    ]

    def __init__(self, brand: str, base_url: str, normalizer: ProductNormalizer | None = None) -> None:
        self.brand = brand
        self.base_url = base_url.rstrip("/")
        self.normalizer = normalizer or ProductNormalizer()

    def search_products(
        self,
        queries: list[str],
        budget: int | None = None,
        limit: int = 60,
    ) -> list[Product]:
        products = self._load_products(limit=250)
        matched: list[Product] = []
        fallback: list[Product] = []

        for raw_product in products:
            product = self._normalize_product(raw_product)
            if product is None or not self._is_boys_product(product):
                continue
            if budget is not None and product.price is not None and product.price > budget:
                continue

            score = max(self._score(product, query) for query in queries) if queries else 1
            product.relevance_score = score

            if score > 0:
                matched.append(product)
            elif self._looks_like_clothing(product):
                product.relevance_score = 0.25
                fallback.append(product)

        chosen = matched if matched else fallback
        chosen = self.normalizer.dedupe(chosen)
        return sorted(chosen, key=lambda item: item.relevance_score, reverse=True)[:limit]

    def _load_products(self, limit: int) -> list[dict]:
        urls = [
            f"{self.base_url}/products.json?limit={limit}",
            f"{self.base_url}/collections/all/products.json?limit={limit}",
        ]
        last_error: Exception | None = None
        context = ssl._create_unverified_context()

        for url in urls:
            try:
                request = Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
                        "Accept": "application/json,text/html,*/*",
                    },
                )
                with urlopen(request, timeout=35, context=context) as response:
                    data = json.loads(response.read().decode("utf-8", errors="ignore"))
                products = data.get("products", [])
                if products:
                    return products
            except Exception as exc:
                last_error = exc
                continue

        if last_error is not None:
            raise last_error
        return []

    def _normalize_product(self, raw_product: dict) -> Product | None:
        title = raw_product.get("title")
        handle = raw_product.get("handle")
        if not title or not handle:
            return None

        variants = raw_product.get("variants") or []
        available_variants = [variant for variant in variants if variant.get("available", True)]
        selected_variants = available_variants or variants

        prices: list[int] = []
        sizes: set[str] = set()
        colors: set[str] = set()

        for variant in selected_variants:
            price = self._parse_price(variant.get("price"))
            if price is not None:
                prices.append(price)

            for value in [variant.get("title"), variant.get("option1"), variant.get("option2"), variant.get("option3")]:
                if not value:
                    continue
                value_text = str(value).strip()
                if re.fullmatch(r"XS|S|M|L|XL|XXL|2XL|3XL|30|32|34|36|38|40", value_text, re.IGNORECASE):
                    sizes.add(value_text.upper())
                for color in self.normalizer.extract_colors(title="", text=value_text):
                    colors.add(color)

        images = raw_product.get("images") or []
        image_url = images[0].get("src") if images else None
        product_url = f"{self.base_url}/products/{handle}"
        body = raw_product.get("body_html") or ""
        tags = " ".join(raw_product.get("tags") or [])

        detected_colors = self.normalizer.extract_colors(title, f"{body} {tags}", product_url)
        colors.update(detected_colors)

        material = self.normalizer.extract_material(f"{title} {body} {tags}")

        return Product(
            brand=self.brand,
            title=title,
            price=min(prices) if prices else None,
            currency="PKR",
            color=sorted(colors)[0] if colors else None,
            colors=sorted(colors),
            sizes=sorted(sizes),
            material=material,
            image_url=image_url,
            product_url=product_url,
            available=bool(available_variants) if variants else None,
            relevance_score=0,
        )

    def _score(self, product: Product, query: str) -> float:
        haystack = " ".join(
            [
                product.title,
                product.color or "",
                " ".join(product.colors),
                product.material or "",
                str(product.product_url or ""),
            ]
        ).lower().replace("-", " ")

        query_words = [
            word
            for word in query.lower().replace("-", " ").split()
            if len(word) > 2 and word not in {"fit", "and", "the", "for"}
        ]
        if not query_words:
            return 1

        score = 0.0
        for word in query_words:
            if word in product.title.lower().replace("-", " "):
                score += 4
            elif word in haystack:
                score += 1.5

        if "shirt" in query.lower() and any(term in haystack for term in ["shirt", "t shirt", "tshirt", "polo"]):
            score += 5
        if "jean" in query.lower() and "jean" in haystack:
            score += 5
        if "pant" in query.lower() and any(term in haystack for term in ["pant", "trouser", "chino"]):
            score += 5

        return score

    @classmethod
    def _is_boys_product(cls, product: Product) -> bool:
        text = f"{product.title} {product.product_url} {product.material or ''} {' '.join(product.colors)}".lower().replace("-", " ")
        if any(term in text for term in cls.BOYS_BLOCKED_TERMS):
            return False

        allowed_terms = [
            "shirt",
            "t shirt",
            "tshirt",
            "polo",
            "button down",
            "jean",
            "pant",
            "trouser",
            "chino",
            "jacket",
            "hoodie",
            "sweatshirt",
        ]
        return any(term in text for term in allowed_terms)

    @staticmethod
    def _looks_like_clothing(product: Product) -> bool:
        text = f"{product.title} {product.product_url} {product.material or ''} {' '.join(product.colors)}".lower().replace("-", " ")
        terms = ["shirt", "t shirt", "tshirt", "polo", "jean", "pant", "trouser", "chino", "jacket", "hoodie", "sweatshirt"]
        return any(term in text for term in terms)

    @staticmethod
    def _parse_price(value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(float(str(value)))
        except ValueError:
            return None
