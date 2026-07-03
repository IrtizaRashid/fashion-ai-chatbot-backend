from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Fashion AI Chatbot Backend",
        description="Phase 0 backend foundation for a Fashion AI Chatbot.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router, prefix="/api", tags=["chat"])

    return app


app = create_app()
