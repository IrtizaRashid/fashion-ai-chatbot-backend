from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router

try:
    from api.analyze import router as analyze_router
except Exception:
    analyze_router = None

try:
    from api.search_products import router as search_products_router
except Exception:
    search_products_router = None

try:
    from api.gemini_chat import router as gemini_chat_router
except Exception:
    gemini_chat_router = None

try:
    from api.memory_chat import router as memory_chat_router
except Exception:
    memory_chat_router = None

try:
    from api.recommend import router as recommend_router
except Exception:
    recommend_router = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Fashion AI Chatbot Backend",
        description="AI Fashion Stylist backend.",
        version="0.5.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router, prefix="/api", tags=["chat"])

    if analyze_router is not None:
        app.include_router(analyze_router, tags=["analysis"])
    if search_products_router is not None:
        app.include_router(search_products_router, tags=["products"])
    if gemini_chat_router is not None:
        app.include_router(gemini_chat_router, tags=["chat"])
    if memory_chat_router is not None:
        app.include_router(memory_chat_router, tags=["conversation"])
    if recommend_router is not None:
        app.include_router(recommend_router, tags=["recommendations"])

    return app


app = create_app()
