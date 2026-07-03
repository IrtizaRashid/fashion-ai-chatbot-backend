"""Main FastAPI application for Phase 3 Body Analysis."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.analyze import router as analyze_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Fashion Stylist - Phase 3",
    description="Body analysis module using Gemini Vision",
    version="0.3.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(analyze_router, tags=["analysis"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AI Fashion Stylist - Body Analysis",
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Fashion Stylist - Phase 3",
        "version": "0.3.0",
        "description": "Body analysis using Gemini Vision",
        "endpoints": {
            "health": "/health",
            "analyze_body": "POST /analyze-body",
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting AI Fashion Stylist Phase 3 server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
