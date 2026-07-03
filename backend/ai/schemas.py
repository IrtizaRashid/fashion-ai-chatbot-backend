"""Pydantic models for body analysis request and response."""

from pydantic import BaseModel, Field, validator
from typing import List


class BodyAnalysisRequest(BaseModel):
    """Request model for body analysis."""

    height: float = Field(..., gt=0, description="Height in cm")
    weight: float = Field(..., gt=0, description="Weight in kg")

    @validator("height")
    def validate_height(cls, v):
        """Validate height is in reasonable range (cm)."""
        if v < 100 or v > 250:
            raise ValueError("Height must be between 100cm and 250cm")
        return v

    @validator("weight")
    def validate_weight(cls, v):
        """Validate weight is in reasonable range (kg)."""
        if v < 30 or v > 300:
            raise ValueError("Weight must be between 30kg and 300kg")
        return v


class BodyAnalysisResponse(BaseModel):
    """Response model for body analysis."""

    body_type: str = Field(
        ..., description="Overall body type estimate (e.g., Athletic, Slim, Heavy)"
    )
    body_build: str = Field(..., description="Overall body build description")
    shoulders: str = Field(..., description="Shoulder appearance and width")
    torso: str = Field(..., description="Torso proportion relative to body")
    legs: str = Field(..., description="Leg proportion and appearance")
    neck: str = Field(..., description="Neck appearance and proportion")
    posture: str = Field(..., description="Posture observations")

    recommended_fit: List[str] = Field(
        default_factory=list, description="Recommended clothing fits"
    )
    recommended_shirts: List[str] = Field(
        default_factory=list, description="Recommended shirt styles"
    )
    recommended_trousers: List[str] = Field(
        default_factory=list, description="Recommended trouser styles"
    )
    recommended_colors: List[str] = Field(
        default_factory=list, description="Recommended colors"
    )
    recommended_patterns: List[str] = Field(
        default_factory=list, description="Recommended patterns"
    )

    avoid: List[str] = Field(
        default_factory=list, description="Clothing styles to avoid"
    )
    summary: str = Field(..., description="Summary of body analysis")
    disclaimer: str = Field(
        ..., description="Disclaimer about visual estimates"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "body_type": "Athletic",
                "body_build": "Balanced muscular build",
                "shoulders": "Moderately broad shoulders",
                "torso": "Proportionate torso with defined waist",
                "legs": "Well-proportioned legs",
                "neck": "Average neck width",
                "posture": "Upright posture observed",
                "recommended_fit": ["Slim fit", "Tailored"],
                "recommended_shirts": ["Oxford shirts", "Crew neck t-shirts"],
                "recommended_trousers": ["Slim chinos", "Dress pants"],
                "recommended_colors": ["Navy", "Black", "Olive"],
                "recommended_patterns": ["Solid colors", "Subtle patterns"],
                "avoid": ["Oversized fits", "Baggy styles"],
                "summary": "Based on your athletic build...",
                "disclaimer": "All observations are visual estimates...",
            }
        }
