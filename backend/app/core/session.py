from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import os
from threading import Lock
from typing import Any

from dotenv import load_dotenv

load_dotenv()

SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "30"))


@dataclass
class SessionData:
    session_id: str
    has_image: bool = False
    height: int | None = None
    weight: int | None = None
    preferences: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class SessionStore:
    def __init__(self, ttl_minutes: int = SESSION_TTL_MINUTES) -> None:
        self._sessions: dict[str, SessionData] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
        self._lock = Lock()

    def get_or_create(self, session_id: str) -> SessionData:
        with self._lock:
            self._remove_expired_sessions()

            session = self._sessions.get(session_id)
            if session is None:
                session = SessionData(session_id=session_id)
                self._sessions[session_id] = session

            session.updated_at = datetime.now(UTC)
            return session

    def update_image_context(
        self,
        session_id: str,
        has_image: bool,
        height: int | None = None,
        weight: int | None = None,
    ) -> SessionData:
        with self._lock:
            session = self._sessions.setdefault(
                session_id,
                SessionData(session_id=session_id),
            )

            if has_image and not session.has_image:
                session.has_image = True

            if height is not None:
                session.height = height

            if weight is not None:
                session.weight = weight

            session.updated_at = datetime.now(UTC)
            return session

    def update_preferences(
        self,
        session_id: str,
        preferences: dict[str, Any],
    ) -> SessionData:
        with self._lock:
            session = self._sessions.setdefault(
                session_id,
                SessionData(session_id=session_id),
            )
            session.preferences.update(preferences)
            session.updated_at = datetime.now(UTC)
            return session

    def _remove_expired_sessions(self) -> None:
        now = datetime.now(UTC)
        expired_session_ids = [
            session_id
            for session_id, session in self._sessions.items()
            if now - session.updated_at > self._ttl
        ]

        for session_id in expired_session_ids:
            del self._sessions[session_id]


_session_store = SessionStore()


def get_session_store() -> SessionStore:
    return _session_store
