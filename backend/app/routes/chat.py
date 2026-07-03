from typing import Annotated, Any

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel, Field

from app.core.session import get_session_store
from app.services.ai_service import (
    analyze_image,
    detect_basic_intent,
    generate_fashion_response,
)


router = APIRouter()
session_store = get_session_store()


class ChatResponse(BaseModel):
    type: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


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
        analysis = await analyze_image(image=image, height=height, weight=weight)
        session = session_store.update_image_context(
            session_id=session_id,
            has_image=True,
            height=height,
            weight=weight,
            analysis=analysis,
        )

        return ChatResponse(
            type="analysis",
            message="Thanks! I analyzed your body profile and saved it for this session.",
            data={
                "body_type": session.body_type,
                "confidence": session.confidence,
                "recommended_size": session.recommended_size,
                "recommendations": session.recommendations,
            },
        )

    if message:
        preferences = detect_basic_intent(message)
        if preferences:
            session = session_store.update_preferences(session_id, preferences)
        else:
            session = session_store.touch_interaction(session_id, "chat")

        ai_response = generate_fashion_response(session, message)

        return ChatResponse(
            type="chat",
            message=ai_response["message"],
            data={
                "body_type": session.body_type,
                "confidence": session.confidence,
                "preferences": session.preferences,
                "recommendations": ai_response["recommendations"],
            },
        )

    session = session_store.touch_interaction(session_id, "chat")
    return ChatResponse(
        type="chat",
        message="Tell me what you are looking for, or upload an image to get started.",
        data={
            "body_type": session.body_type,
            "confidence": session.confidence,
            "preferences": session.preferences,
            "recommendations": session.recommendations,
        },
    )
