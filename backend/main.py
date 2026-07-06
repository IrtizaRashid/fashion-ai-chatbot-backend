"""Main FastAPI application for AI Fashion Stylist."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analyze import router as analyze_router
from api.gemini_chat import router as gemini_chat_router
from api.memory_chat import router as memory_chat_router
from api.recommend import router as recommend_router
from api.search_products import router as search_products_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Fashion Stylist",
    description="Body analysis, product search, recommendation ranking, Redis memory, and Gemini text chat",
    version="0.8.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, tags=["analysis"])
app.include_router(search_products_router, tags=["products"])
app.include_router(recommend_router, tags=["recommendations"])
app.include_router(memory_chat_router, tags=["conversation"])
app.include_router(gemini_chat_router, tags=["chat"])


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "AI Fashion Stylist",
    }


@app.get("/")
async def root():
    return {
        "name": "AI Fashion Stylist",
        "version": "0.8.0",
        "endpoints": {
            "health": "/health",
            "analyze_body": "POST /analyze-body",
            "search_products": "POST /search-products",
            "recommend": "POST /recommend",
            "memory_chat": "POST /chat",
            "chat_gemini": "POST /chat-gemini",
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting AI Fashion Stylist server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
