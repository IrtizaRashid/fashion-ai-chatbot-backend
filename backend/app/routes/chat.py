from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from app.core.session import get_session_store
from app.services.ai_service import detect_basic_intent


router = APIRouter()
session_store = get_session_store()


class ChatResponse(BaseModel):
    type: str
    message: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    session_id: Annotated[str, Form(...)],
    message: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
    height: Annotated[int | None, Form()] = None,
    weight: Annotated[int | None, Form()] = None,
) -> ChatResponse:
    session = session_store.get_or_create(session_id)

    if image is not None:
        session_store.update_image_context(
            session_id=session_id,
            has_image=not session.has_image,
            height=height,
            weight=weight,
        )

        return ChatResponse(
            type="analysis_start",
            message="Thanks! I’m analyzing your body type...",
        )

    if message:
        preferences = detect_basic_intent(message)
        if preferences:
            session_store.update_preferences(session_id, preferences)

        return ChatResponse(
            type="chat",
            message="Got it. I’ll adjust recommendations based on your preferences.",
        )

    return ChatResponse(
        type="chat",
        message="Tell me what you’re looking for, or upload an image to get started.",
    )
