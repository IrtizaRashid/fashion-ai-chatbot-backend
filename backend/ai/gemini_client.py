"""Gemini Vision API client."""

import base64
import json
import logging
from typing import Optional
import google.generativeai as genai
from core.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Gemini Vision API."""

    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        """Initialize Gemini client with API key."""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def analyze_image_with_text(
        self, image_data: bytes, prompt: str
    ) -> Optional[dict]:
        """
        Send image and text prompt to Gemini Vision.

        Args:
            image_data: Image file bytes
            prompt: Text prompt for analysis

        Returns:
            Parsed JSON response or None if failed

        Raises:
            ValueError: If image data is invalid
            RuntimeError: If Gemini API call fails
        """

        try:
            # Encode image to base64
            image_b64 = base64.standard_b64encode(image_data).decode("utf-8")

            # Create image part for API
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_b64,
            }

            # Call Gemini Vision API
            logger.info("Sending request to Gemini Vision API...")
            response = self.model.generate_content([prompt, image_part])

            # Get response text
            response_text = response.text

            if not response_text:
                raise RuntimeError("Empty response from Gemini API")

            logger.info("Received response from Gemini API")

            # Parse JSON response
            try:
                # Try to extract JSON if there's extra text
                if response_text.startswith("{"):
                    json_str = response_text
                else:
                    # Find JSON object in response
                    start_idx = response_text.find("{")
                    end_idx = response_text.rfind("}") + 1
                    if start_idx == -1 or end_idx == 0:
                        raise ValueError("No JSON found in response")
                    json_str = response_text[start_idx:end_idx]

                parsed_json = json.loads(json_str)
                logger.info("Successfully parsed Gemini response")
                return parsed_json

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response_text}")
                raise RuntimeError(
                    f"Failed to parse Gemini response as JSON: {str(e)}"
                )

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise RuntimeError(f"Gemini API call failed: {str(e)}")


# Singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
