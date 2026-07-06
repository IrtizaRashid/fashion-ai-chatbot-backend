"""In-memory conversation session model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from conversation.schemas import ConversationMessage
from recommendation.schemas import BodyAnalysis, Recommendation


@dataclass
class ConversationMemory:
    session_id: str
    expires_at: datetime
    body_analysis: BodyAnalysis | None = None
    preferences: dict[str, Any] = field(default_factory=dict)
    conversation_history: list[ConversationMessage] = field(default_factory=list)
    current_recommendations: list[Recommendation] = field(default_factory=list)
    current_filtered_recommendations: list[Recommendation] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str) -> None:
        self.conversation_history.append(ConversationMessage(role=role, content=content))
        self.last_interaction = datetime.utcnow()

    def set_recommendations(self, recommendations: list[Recommendation]) -> None:
        self.current_recommendations = recommendations
        self.current_filtered_recommendations = recommendations
        self.last_interaction = datetime.utcnow()
