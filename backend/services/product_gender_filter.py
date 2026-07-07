"""Men-only product filtering for scraped/catalog products."""

from __future__ import annotations

from typing import Any
import re


BLOCKED_TERMS = {
    "girl",
    "girls",
    "woman",
    "women",
    "ladies",
    "female",
    "feminine",
    "cropped",
    "crop top",
    "super cropped",
    "lace",
    "lace detail",
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
    "baby girl",
    "kids girls",
    "/women",
    "/woman",
    "/girls",
    "/girl",
    "/ladies",
    "women-",
    "woman-",
    "girls-",
    "girl-",
}

MEN_SIGNALS = {
    "men",
    "mens",
    "men's",
    "boys",
    "boy",
    "male",
    "man",
    "gent",
    "gents",
    "regular fit",
    "slim fit",
    "straight fit",
    "button down",
    "oxford",
    "polo",
    "dress shirt",
    "formal shirt",
    "casual shirt",
    "trouser",
    "trousers",
    "chino",
    "chinos",
    "jeans",
    "denim pant",
    "cargo pant",
}

MEN_CATEGORIES = {
    "/men",
    "/mens",
    "/men-",
    "/mens-",
    "/boys",
    "/boy",
    "men_",
    "mens_",
    "boys_",
    "man-",
    "gents",
}

NEUTRAL_MENS_ALLOWED = {
    "shirt",
    "t shirt",
    "t-shirt",
    "tshirt",
    "polo",
    "button down",
    "oxford",
    "jean",
    "jeans",
    "pant",
    "pants",
    "trouser",
    "trousers",
    "chino",
    "chinos",
    "jacket",
    "hoodie",
    "sweatshirt",
}


def normalize_text(*values: Any) -> str:
    parts: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            parts.extend(str(item) for item in value if item is not None)
        else:
            parts.append(str(value))
    return " ".join(parts).lower().replace("-", " ").replace("_", " ")


def is_mens_product(product: Any, extra_text: str = "") -> bool:
    """Return True only for products safe to show in a men's fashion app."""
    text = normalize_text(
        getattr(product, "brand", ""),
        getattr(product, "title", ""),
        getattr(product, "color", ""),
        getattr(product, "colors", []),
        getattr(product, "material", ""),
        getattr(product, "product_url", ""),
        extra_text,
    )

    if not text.strip():
        return False
    if any(term.replace("-", " ") in text for term in BLOCKED_TERMS):
        return False

    url_text = normalize_text(getattr(product, "product_url", ""), extra_text)
    if any(_contains_phrase(url_text, term) for term in MEN_CATEGORIES):
        return True
    if any(_contains_phrase(text, signal) for signal in MEN_SIGNALS):
        return True

    # Strict men-only mode: neutral items like "Graphic T-Shirt" are rejected unless
    # the store metadata, URL, title, or tags clearly say Men/Boys.
    return False


def _contains_phrase(text: str, phrase: str) -> bool:
    clean_phrase = phrase.lower().replace("-", " ").replace("_", " ").strip()
    if not clean_phrase:
        return False
    if clean_phrase.startswith("/"):
        return clean_phrase.replace("/", " ").strip() in text
    return re.search(rf"(?<![a-z0-9]){re.escape(clean_phrase)}(?![a-z0-9])", text) is not None

def filter_mens_products(products: list[Any]) -> list[Any]:
    return [product for product in products if is_mens_product(product)]

COLOR_ALIASES = {
    "grey": {"grey", "gray", "gry"},
    "gray": {"grey", "gray", "gry"},
    "white": {"white", "wht", "off white", "offwhite"},
    "black": {"black", "blk"},
    "blue": {"blue", "blu"},
    "navy": {"navy", "nvy"},
    "green": {"green", "grn"},
    "brown": {"brown", "brn"},
    "olive": {"olive", "olv"},
    "khaki": {"khaki", "kha"},
}


def _color_terms(colors: list[str]) -> set[str]:
    terms: set[str] = set()
    for color in colors:
        key = str(color).strip().lower().replace("-", " ")
        if not key:
            continue
        terms.add(key)
        terms.update(COLOR_ALIASES.get(key, set()))
    return terms


def product_matches_any_color(product: Any, colors: list[str], extra_text: str = "") -> bool:
    """Return True when a product explicitly matches at least one requested color."""
    if not colors:
        return True

    requested = _color_terms(colors)
    detected_colors = _color_terms(
        [
            str(value)
            for value in [getattr(product, "color", ""), *list(getattr(product, "colors", []) or [])]
            if value
        ]
    )

    # If the scraper detected color values, trust those first. This prevents a product
    # with a white variant URL from showing as Blue/Red when the user asked for white.
    if detected_colors:
        return bool(requested.intersection(detected_colors))

    text = normalize_text(getattr(product, "title", ""), getattr(product, "product_url", ""), extra_text)
    return any(term in text for term in requested)


def filter_products_by_color(products: list[Any], colors: list[str]) -> list[Any]:
    if not colors:
        return products

    filtered: list[Any] = []
    display_color = str(colors[0]).strip().title() if len(colors) == 1 else None
    for product in products:
        if not product_matches_any_color(product, colors):
            continue
        if display_color and hasattr(product, "color"):
            product.color = "Grey" if display_color == "Gray" else display_color
            existing_colors = list(getattr(product, "colors", []) or [])
            if product.color not in existing_colors and hasattr(product, "colors"):
                product.colors = [product.color, *existing_colors]
        filtered.append(product)
    return filtered

TOP_TERMS = {"shirt", "t shirt", "tshirt", "tee", "polo", "oxford", "button down"}
BOTTOM_TERMS = {"pant", "pants", "trouser", "trousers", "jean", "jeans", "chino", "chinos", "short", "shorts"}


def _requested_category_terms(requested_items: list[str]) -> set[str]:
    requested_text = normalize_text(requested_items)
    terms: set[str] = set()
    if any(term in requested_text for term in ["shirt", "t shirt", "tshirt", "tee", "polo", "oxford"]):
        terms.update(TOP_TERMS)
    if any(term in requested_text for term in ["pant", "trouser", "jean", "chino", "short"]):
        terms.update(BOTTOM_TERMS)
    return terms


def product_matches_category(product: Any, requested_items: list[str]) -> bool:
    terms = _requested_category_terms(requested_items)
    if not terms:
        return True
    text = normalize_text(getattr(product, "title", ""), getattr(product, "product_url", ""))

    if terms.intersection(TOP_TERMS):
        blocked_for_tops = {"tank", "short", "shorts", "pant", "pants", "trouser", "jean", "chino", "hoodie", "sweatshirt"}
        if any(_contains_phrase(text, term) for term in blocked_for_tops):
            return False
        return any(_contains_phrase(text, term) for term in TOP_TERMS)

    if terms.intersection(BOTTOM_TERMS):
        blocked_for_bottoms = {"shirt", "t shirt", "tshirt", "tee", "polo", "hoodie", "sweatshirt"}
        if any(_contains_phrase(text, term) for term in blocked_for_bottoms):
            return False
        return any(_contains_phrase(text, term) for term in BOTTOM_TERMS)

    return True


def filter_products_by_category(products: list[Any], requested_items: list[str]) -> list[Any]:
    if not requested_items:
        return products
    return [product for product in products if product_matches_category(product, requested_items)]
