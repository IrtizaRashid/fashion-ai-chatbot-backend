import os
import traceback

from fastapi import APIRouter

from models.product import ProductSearchRequest, ProductSearchResponse
from services.product_normalizer import ProductNormalizer
from services.product_gender_filter import filter_mens_products, filter_products_by_color, filter_products_by_category
from services.query_generator import QueryGenerator
from services.shopify_fallback import ShopifyFallbackClient

router = APIRouter()


def _collect_products(request: ProductSearchRequest):
    normalizer = ProductNormalizer()
    generated_queries = QueryGenerator().generate(request)
    queries = generated_queries or ["Shirt", "Black Shirt"]

    products = []
    debug = {
        "route_file": __file__,
        "cwd": os.getcwd(),
        "queries": queries,
        "budget": request.budget,
        "sources": [],
    }

    for brand, base_url in [
        ("Breakout", "https://www.breakout.com.pk"),
        ("Outfitters", "https://outfitters.com.pk"),
    ]:
        source_info = {"brand": brand, "base_url": base_url, "count": 0, "error": None, "sample": []}
        try:
            source_products = ShopifyFallbackClient(brand, base_url, normalizer).search_products(
                queries=queries,
                budget=request.budget,
                limit=60,
            )
            source_info["count"] = len(source_products)
            source_info["sample"] = [
                {
                    "title": product.title,
                    "price": product.price,
                    "url": str(product.product_url),
                }
                for product in source_products[:3]
            ]
            products.extend(source_products)
        except Exception:
            source_info["error"] = traceback.format_exc()
        debug["sources"].append(source_info)

    products = filter_mens_products(normalizer.dedupe(products))
    products = filter_products_by_category(products, request.recommended_shirts)
    products = filter_products_by_color(products, request.recommended_colors)
    products = sorted(products, key=lambda product: product.relevance_score, reverse=True)
    debug["final_count"] = len(products)
    return products, debug


@router.post("/search-products", response_model=ProductSearchResponse)
async def search_products(request: ProductSearchRequest) -> ProductSearchResponse:
    products, _debug = _collect_products(request)
    return ProductSearchResponse(products=products)


@router.post("/search-products-debug")
async def search_products_debug(request: ProductSearchRequest):
    products, debug = _collect_products(request)
    debug["products"] = [
        {
            "brand": product.brand,
            "title": product.title,
            "price": product.price,
            "color": product.color,
            "product_url": str(product.product_url),
        }
        for product in products[:10]
    ]
    return debug



