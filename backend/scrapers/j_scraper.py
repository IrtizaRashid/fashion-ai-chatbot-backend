from models.product import Product
from scrapers.base_scraper import BaseScraper


class JScraper(BaseScraper):
    brand = "J."
    base_url = "https://www.junaidjamshed.com"
    search_path = "/catalogsearch/result/?q={query}"

    async def search_products(self, queries: list[str], budget: int | None = None) -> list[Product]:
        return await self._search_with_playwright(queries, budget)
