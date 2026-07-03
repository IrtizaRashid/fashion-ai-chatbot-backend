"""Body analysis API endpoints."""

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ai.body_analyzer import analyze_body
from ai.schemas import BodyAnalysisResponse
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze-body", response_model=BodyAnalysisResponse)
async def analyze_body_endpoint(
    image: UploadFile = File(..., description="User photo for analysis"),
    height: float = Form(..., gt=0, description="Height in cm"),
    weight: float = Form(..., gt=0, description="Weight in kg"),
) -> BodyAnalysisResponse:
    """
    Analyze user's body shape and proportions.

    Accepts an image and basic measurements, returns detailed body analysis.

    Args:
        image: JPEG, PNG, or WEBP image file
        height: Height in centimeters
        weight: Weight in kilograms

    Returns:
        BodyAnalysisResponse with styling recommendations

    Raises:
        HTTPException: 400 for validation errors
        HTTPException: 413 for oversized files
        HTTPException: 415 for unsupported image types
        HTTPException: 500 for server errors
    """

    logger.info(
        f"Received analyze-body request: height={height}, weight={weight}"
    )

    try:
        # Validate image file exists
        if not image:
            logger.error("No image file provided")
            raise HTTPException(
                status_code=400, detail="Image file is required"
            )

        # Validate image type
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            logger.error(
                f"Invalid image type: {image.content_type}"
            )
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported image type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
            )

        # Read image data
        image_data = image.file.read()

        # Validate image size
        if len(image_data) > settings.MAX_IMAGE_SIZE:
            logger.error(
                f"Image too large: {len(image_data)} bytes"
            )
            raise HTTPException(
                status_code=413,
                detail=f"Image file too large. Maximum size: {settings.MAX_IMAGE_SIZE / (1024 * 1024):.0f}MB",
            )

        if not image_data:
            logger.error("Image file is empty")
            raise HTTPException(
                status_code=400, detail="Image file is empty"
            )

        # Validate height and weight
        try:
            if height <= 0:
                raise ValueError("Height must be positive")
            if height < 100 or height > 250:
                raise ValueError(
                    "Height must be between 100cm and 250cm"
                )

            if weight <= 0:
                raise ValueError("Weight must be positive")
            if weight < 30 or weight > 300:
                raise ValueError("Weight must be between 30kg and 300kg")

        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        # Call body analyzer
        logger.info("Calling body analyzer...")
        analysis = await analyze_body(image_data, height, weight)

        logger.info("Body analysis completed successfully")
        return analysis

    except HTTPException:
        raise

    except ValueError as e:
        logger.error(f"Input validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except RuntimeError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze body. Please try again.",
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again.",
        )
