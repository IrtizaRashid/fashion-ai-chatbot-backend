"""Pydantic schemas for the recommendation ranking engine."""

from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


RecommendationLevel = Literal["Excellent", "Good", "Fair", "Poor"]


class BodyAnalysis(BaseModel):
    body_type: str = Field(..., min_length=1)
    body_build: str | None = None
    recommended_fit: list[str] = Field(default_factory=list)
    recommended_colors: list[str] = Field(default_factory=list)
    recommended_patterns: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    summary: str | None = None


class ProductInput(BaseModel):
    brand: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    price: int | None = Field(default=None, ge=0)
    currency: str = "PKR"
    color: str | None = None
    colors: list[str] = Field(default_factory=list)
    material: str | None = None
    sizes: list[str] = Field(default_factory=list)
    product_url: HttpUrl | str | None = None
    image_url: HttpUrl | str | None = None
    available: bool | None = None
    relevance_score: float | None = None

    @field_validator("colors", "sizes", mode="before")
    @classmethod
    def normalize_lists(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return list(value)


class RecommendationRequest(BaseModel):
    body_analysis: BodyAnalysis
    products: list[ProductInput] = Field(..., min_length=1)
    budget: int | None = Field(default=None, ge=0)
    occasion: str | None = None

    @model_validator(mode="after")
    def validate_products(self) -> "RecommendationRequest":
        if not self.products:
            raise ValueError("At least one product is required")
        return self


class Recommendation(BaseModel):
    brand: str
    title: str
    match_score: int = Field(..., ge=0, le=100)
    recommendation: RecommendationLevel
    reason: str = Field(..., min_length=1)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    product_url: HttpUrl | str | None = None
    image_url: HttpUrl | str | None = None
    price: int | None = None
    currency: str = "PKR"
    color: str | None = None
    sizes: list[str] = Field(default_factory=list)
    material: str | None = None


class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]
