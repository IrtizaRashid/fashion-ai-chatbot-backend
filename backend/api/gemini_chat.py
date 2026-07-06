"""Gemini-powered text chat endpoint for fashion follow-up questions."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai

from core.config import settings


router = APIRouter()


class GeminiChatRequest(BaseModel):
    message: str
    analysis: dict[str, Any] | None = Field(default=None)


class GeminiChatResponse(BaseModel):
    message: str


def _build_prompt(message: str, analysis: dict[str, Any] | None) -> str:
    return f"""
You are an AI fashion stylist chatbot for Pakistani users.

Answer the user's message directly and conversationally.
Use the body/style analysis context when available.

Rules:
- Keep answers short: 3 to 7 lines.
- If the user asks for websites, brands, stores, shopping, or where to buy, mention these supported Pakistani websites:
  Outfitters: https://outfitters.com.pk
  Breakout: https://www.breakout.com.pk
  J.: https://www.junaidjamshed.com
- Do not invent product availability.
- Do not rank products.
- Do not give medical advice.
- If the user asks for budget, fit, color, outfit, casual, office, party, wedding, shirts, trousers, or what to avoid, answer specifically.

Analysis context:
{analysis or {}}

User message:
{message}
"""


@router.post("/chat-gemini", response_model=GeminiChatResponse)
async def chat_gemini(request: GeminiChatRequest) -> GeminiChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(_build_prompt(request.message, request.analysis))
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return GeminiChatResponse(message=text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini chat failed: {exc}") from exc
