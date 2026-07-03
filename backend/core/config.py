"""Configuration and environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment variables."""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Max file size: 10MB
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024

    # Allowed image types
    ALLOWED_IMAGE_TYPES: set = {"image/jpeg", "image/png", "image/webp"}

    def __init__(self):
        """Validate required settings."""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")


settings = Settings()
