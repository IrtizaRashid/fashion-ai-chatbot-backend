"""Body analysis module using Gemini Vision."""

import logging
from typing import Optional
from ai.gemini_client import get_gemini_client
from ai.prompts import get_body_analysis_prompt
from ai.schemas import BodyAnalysisResponse

logger = logging.getLogger(__name__)


async def analyze_body(
    image_data: bytes,
    height: float,
    weight: float,
    mime_type: str = "image/jpeg",
    gemini_api_key: Optional[str] = None,
) -> BodyAnalysisResponse:
    """
    Analyze body shape and proportions using Gemini Vision.

    Args:
        image_data: Image file bytes
        height: User's height in centimeters
        weight: User's weight in kilograms
        gemini_api_key: Optional user-provided Gemini API key

    Returns:
        BodyAnalysisResponse with validated analysis

    Raises:
        ValueError: If input validation fails
        RuntimeError: If Gemini API fails
    """

    logger.info(f"Starting body analysis: height={height}cm, weight={weight}kg")

    # Validate inputs
    if not image_data:
        logger.error("No image data provided")
        raise ValueError("Image data is required")

    if height <= 0:
        logger.error(f"Invalid height: {height}")
        raise ValueError("Height must be positive")

    if weight <= 0:
        logger.error(f"Invalid weight: {weight}")
        raise ValueError("Weight must be positive")

    try:
        # Get Gemini client (use user key if provided, otherwise use default)
        gemini_client = get_gemini_client(api_key=gemini_api_key)

        # Generate prompt
        prompt = get_body_analysis_prompt(height, weight)

        # Call Gemini Vision API
        logger.info("Calling Gemini Vision API for body analysis...")
        response_data = gemini_client.analyze_image_with_text(
            image_data, prompt, mime_type
        )

        if not response_data:
            logger.error("Gemini returned empty response")
            raise RuntimeError("Gemini returned empty response")

        # Validate response with Pydantic model
        logger.info("Validating response against schema...")
        analysis = BodyAnalysisResponse(**response_data)

        logger.info("Body analysis completed successfully")
        return analysis

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Body analysis failed: {str(e)}")
        raise RuntimeError(f"Body analysis failed: {str(e)}")
