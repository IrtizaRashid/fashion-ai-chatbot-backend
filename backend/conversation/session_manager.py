"""Session manager with TTL-based in-memory storage."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from threading import RLock

from conversation.memory import ConversationMemory
from conversation.schemas import SessionResponse
from recommendation.schemas import BodyAnalysis, Recommendation


class SessionExpiredError(KeyError):
    """Raised when a session exists but is expired."""


class SessionNotFoundError(KeyError):
    """Raised when a session does not exist."""


class SessionManager:
    def __init__(self, ttl_minutes: int | None = None) -> None:
        self.ttl_minutes = ttl_minutes or int(os.getenv("CONVERSATION_TTL_MINUTES", "30"))
        self._sessions: dict[str, ConversationMemory] = {}
        self._lock = RLock()

    def create_or_update(
        self,
        session_id: str,
        body_analysis: BodyAnalysis | None = None,
        recommendations: list[Recommendation] | None = None,
    ) -> ConversationMemory:
        with self._lock:
            self.cleanup_expired()
            session = self._sessions.get(session_id)
            if session is None:
                session = ConversationMemory(session_id=session_id, expires_at=self._new_expiry())
                self._sessions[session_id] = session

            session.expires_at = self._new_expiry()
            if body_analysis is not None:
                session.body_analysis = body_analysis
            if recommendations is not None:
                session.set_recommendations(recommendations)
            return session

    def get(self, session_id: str) -> ConversationMemory:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise SessionNotFoundError(session_id)
            if session.expires_at <= datetime.utcnow():
                del self._sessions[session_id]
                raise SessionExpiredError(session_id)
            session.expires_at = self._new_expiry()
            return session

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def cleanup_expired(self) -> None:
        now = datetime.utcnow()
        expired = [session_id for session_id, session in self._sessions.items() if session.expires_at <= now]
        for session_id in expired:
            del self._sessions[session_id]

    def to_response(self, session: ConversationMemory) -> SessionResponse:
        return SessionResponse(
            session_id=session.session_id,
            body_analysis=session.body_analysis,
            preferences=session.preferences,
            conversation_history=session.conversation_history,
            current_recommendations=session.current_recommendations,
            current_filtered_recommendations=session.current_filtered_recommendations,
            expires_at=session.expires_at,
        )

    def _new_expiry(self) -> datetime:
        return datetime.utcnow() + timedelta(minutes=self.ttl_minutes)


session_manager = SessionManager()
