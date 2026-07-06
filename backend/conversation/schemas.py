"""Schemas for conversation memory and smart filtering."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from recommendation.schemas import BodyAnalysis, Recommendation


class FilterCriteria(BaseModel):
    brand: str | None = None
    exclude_brand: str | None = None
    color: str | None = None
    material: str | None = None
    max_price: int | None = Field(default=None, ge=0)
    min_price: int | None = Field(default=None, ge=0)
    fit: str | None = None
    pattern: str | None = None
    category: str | None = None
    available: bool | None = None
    occasion: str | None = None
    sort: str | None = None
    reset_filters: bool = False


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    body_analysis: BodyAnalysis | None = None
    recommendations: list[Recommendation] | None = None


class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation] = Field(default_factory=list)
    filters: FilterCriteria | None = None
    session_id: str


class SessionCreateRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    body_analysis: BodyAnalysis | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)


class SessionResponse(BaseModel):
    session_id: str
    body_analysis: BodyAnalysis | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    current_recommendations: list[Recommendation] = Field(default_factory=list)
    current_filtered_recommendations: list[Recommendation] = Field(default_factory=list)
    expires_at: datetime

    @model_validator(mode="after")
    def ensure_filtered_list(self) -> "SessionResponse":
        if not self.current_filtered_recommendations and self.current_recommendations:
            self.current_filtered_recommendations = self.current_recommendations
        return self
