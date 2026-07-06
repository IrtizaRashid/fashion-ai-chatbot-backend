import logging

from models.product import Product
from scrapers.base_scraper import BaseScraper
from services.shopify_fallback import ShopifyFallbackClient

logger = logging.getLogger(__name__)


class OutfittersScraper(BaseScraper):
    brand = "Outfitters"
    base_url = "https://outfitters.com.pk"
    search_path = "/search?q={query}"

    async def search_products(self, queries: list[str], budget: int | None = None) -> list[Product]:
        products: list[Product] = []
        try:
            products = await self._search_with_playwright(queries, budget)
        except Exception as exc:
            logger.warning("%s Playwright scraper failed, using fallback: %s", self.brand, exc)

        if len(products) >= self.min_products_per_brand:
            return products

        try:
            fallback = ShopifyFallbackClient(self.brand, self.base_url, self.normalizer)
            fallback_products = fallback.search_products(queries, budget, limit=60)
            return self.normalizer.dedupe([*products, *fallback_products])
        except Exception as exc:
            logger.warning("%s Shopify fallback failed: %s", self.brand, exc)
            return products
