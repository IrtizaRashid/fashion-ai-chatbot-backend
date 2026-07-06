import asyncio
import logging

from models.product import Product, ProductSearchRequest
from scrapers.j_scraper import JScraper
from services.product_normalizer import ProductNormalizer
from services.query_generator import QueryGenerator
from services.shopify_fallback import ShopifyFallbackClient

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        query_generator: QueryGenerator | None = None,
        normalizer: ProductNormalizer | None = None,
    ) -> None:
        self.query_generator = query_generator or QueryGenerator()
        self.normalizer = normalizer or ProductNormalizer()

    async def search(self, recommendations: ProductSearchRequest) -> list[Product]:
        queries = self.query_generator.generate(recommendations)
        if not queries:
            return []

        results = await asyncio.gather(
            self._safe_shopify("Breakout", "https://www.breakout.com.pk", queries, recommendations.budget),
            self._safe_shopify("Outfitters", "https://outfitters.com.pk", queries, recommendations.budget),
            self._safe_j_scrape(queries, recommendations.budget),
        )

        products = [product for brand_products in results for product in brand_products]
        products = self.normalizer.dedupe(products)
        return sorted(products, key=lambda product: product.relevance_score, reverse=True)

    async def _safe_shopify(
        self,
        brand: str,
        base_url: str,
        queries: list[str],
        budget: int | None,
    ) -> list[Product]:
        try:
            return await asyncio.to_thread(
                ShopifyFallbackClient(brand, base_url, self.normalizer).search_products,
                queries,
                budget,
                60,
            )
        except Exception as exc:
            logger.exception("%s Shopify product extraction failed: %s", brand, exc)
            return []

    async def _safe_j_scrape(self, queries: list[str], budget: int | None) -> list[Product]:
        try:
            return await JScraper(self.normalizer, timeout_ms=20_000).search_products(queries, budget)
        except Exception as exc:
            logger.exception("J. product extraction failed: %s", exc)
            return []
