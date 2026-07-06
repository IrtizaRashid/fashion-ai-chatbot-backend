from abc import ABC, abstractmethod
import asyncio
import logging
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from models.product import Product
from services.product_normalizer import ProductNormalizer

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    brand: str
    base_url: str
    search_path: str = "/search?q={query}"
    product_selectors: tuple[str, ...] = (
        "[data-product-id]",
        ".product-card",
        ".product-item",
        ".grid-product",
        ".card-wrapper",
        ".product",
        "li.product",
        "[class*='product-card']",
        "[class*='product-item']",
        "[class*='card']",
    )

    def __init__(
        self,
        normalizer: ProductNormalizer | None = None,
        timeout_ms: int = 30_000,
        min_products_per_brand: int = 20,
    ) -> None:
        self.normalizer = normalizer or ProductNormalizer()
        self.timeout_ms = timeout_ms
        self.min_products_per_brand = min_products_per_brand

    @abstractmethod
    async def search_products(self, queries: list[str], budget: int | None = None) -> list[Product]:
        raise NotImplementedError

    async def _search_with_playwright(
        self,
        queries: list[str],
        budget: int | None = None,
    ) -> list[Product]:
        products: list[Product] = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            try:
                page = await browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/121.0.0.0 Safari/537.36"
                    )
                )
                for query in queries:
                    try:
                        html = await self._fetch_search_html(page, query)
                        products.extend(self._parse_products(html, query, budget))
                    except Exception as exc:
                        logger.warning("%s failed query '%s': %s", self.brand, query, exc)

                    products = self.normalizer.dedupe(products)
                    if len(products) >= self.min_products_per_brand:
                        break
            finally:
                await browser.close()

        return sorted(self.normalizer.dedupe(products), key=lambda product: product.relevance_score, reverse=True)

    async def _fetch_search_html(self, page, query: str) -> str:
        url = self.search_url(query)
        logger.info("Searching %s products: %s", self.brand, url)

        await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
        try:
            await page.wait_for_load_state("networkidle", timeout=12_000)
        except PlaywrightTimeoutError:
            logger.debug("%s networkidle timeout for query '%s'", self.brand, query)

        await self._scroll_page(page)
        return await page.content()

    async def _scroll_page(self, page) -> None:
        for _ in range(5):
            await page.mouse.wheel(0, 1800)
            await asyncio.sleep(0.5)

    def search_url(self, query: str) -> str:
        return f"{self.base_url}{self.search_path.format(query=quote_plus(query))}"

    def _parse_products(self, html: str, query: str, budget: int | None = None) -> list[Product]:
        soup = BeautifulSoup(html, "html.parser")
        cards = self._find_product_cards(soup)
        products: list[Product] = []

        for card in cards:
            product = self._extract_product(card, query)
            if product is None:
                continue
            if budget is not None and product.price is not None and product.price > budget:
                continue
            products.append(product)

        return sorted(products, key=lambda product: product.relevance_score, reverse=True)

    def _find_product_cards(self, soup: BeautifulSoup):
        candidates = []
        for selector in self.product_selectors:
            candidates.extend(soup.select(selector))

        for link in soup.select("a[href]"):
            href = self.normalizer.absolute_url(self.base_url, link.get("href"))
            if not self.normalizer.is_product_url(href):
                continue
            parent = link
            for _ in range(4):
                parent = parent.find_parent(["article", "li", "div"])
                if not parent:
                    break
                candidates.append(parent)

        unique = []
        seen = set()
        for card in candidates:
            marker = id(card)
            if marker in seen:
                continue
            seen.add(marker)
            if self._card_has_product_signal(card):
                unique.append(card)
        return unique

    def _card_has_product_signal(self, card) -> bool:
        link = card.select_one("a[href]")
        image = card.select_one("img")
        text = card.get_text(" ", strip=True)
        product_url = self.normalizer.absolute_url(self.base_url, link.get("href")) if link else None
        return bool(link and image and self.normalizer.is_product_url(product_url) and self.normalizer.normalize_price(text))

    def _extract_product(self, card, query: str) -> Product | None:
        text = card.get_text(" ", strip=True)
        title = self._extract_title(card)
        price = self.normalizer.normalize_price(text)
        product_url = self._extract_product_url(card)
        image_url = self._extract_image_url(card)

        if not title or price is None or not product_url or not image_url:
            return None
        if not self.normalizer.is_product_url(product_url):
            return None

        score = self._relevance_score(title, text, query)
        if score <= 0:
            return None

        colors = self.normalizer.extract_colors(title, text, product_url)
        return Product(
            brand=self.brand,
            title=title,
            price=price,
            color=colors[0] if colors else None,
            colors=colors,
            sizes=self.normalizer.extract_sizes(text),
            material=self.normalizer.extract_material(text),
            image_url=image_url,
            product_url=product_url,
            available=self._extract_availability(text),
            relevance_score=score,
        )

    def _extract_title(self, card) -> str | None:
        selectors = [".product-title", ".card__heading", ".product-card__title", ".name", ".title", "h3", "h2", "a[title]"]
        for selector in selectors:
            element = card.select_one(selector)
            if not element:
                continue
            title = element.get("title") or element.get_text(" ", strip=True)
            if title and len(title.strip()) > 2:
                return " ".join(title.split())

        image = card.select_one("img[alt]")
        if image and image.get("alt"):
            return " ".join(image["alt"].split())
        return None

    def _extract_product_url(self, card) -> str | None:
        for link in card.select("a[href]"):
            url = self.normalizer.absolute_url(self.base_url, link.get("href"))
            if self.normalizer.is_product_url(url):
                return url
        return None

    def _extract_image_url(self, card) -> str | None:
        image = card.select_one("img")
        if not image:
            return None
        src = image.get("src") or image.get("data-src") or image.get("data-original") or image.get("data-lazy-src")
        return self.normalizer.absolute_url(self.base_url, src)

    def _extract_availability(self, text: str) -> bool | None:
        lowered = text.lower()
        if "sold out" in lowered or "out of stock" in lowered or "unavailable" in lowered:
            return False
        if "add to cart" in lowered or "choose options" in lowered or "in stock" in lowered:
            return True
        return None

    def _relevance_score(self, title: str, text: str, query: str) -> float:
        haystack = f"{title} {text}".lower().replace("-", " ")
        query_words = [
            word
            for word in query.lower().replace("-", " ").split()
            if len(word) > 2 and word not in {"fit", "and", "the", "for"}
        ]
        if not query_words:
            return 1

        score = 0.0
        title_lower = title.lower().replace("-", " ")
        for word in query_words:
            if word in title_lower:
                score += 4
            elif word in haystack:
                score += 1.5

        if "shirt" in query.lower() and "shirt" in title_lower:
            score += 5
        if "polo" in query.lower() and "polo" in title_lower:
            score += 5
        if "oxford" in query.lower() and "oxford" in title_lower:
            score += 5

        return score
