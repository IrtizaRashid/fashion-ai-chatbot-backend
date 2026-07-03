from typing import Any


COLOR_KEYWORDS = {"blue", "black", "white"}
FIT_KEYWORDS = {"loose", "tight", "regular"}
BUDGET_KEYWORDS = {"budget", "under", "cheap"}


def detect_basic_intent(message: str) -> dict[str, Any]:
    normalized_message = message.lower()
    preferences: dict[str, Any] = {}

    if any(keyword in normalized_message for keyword in BUDGET_KEYWORDS):
        preferences["budget"] = 4000

    for color in COLOR_KEYWORDS:
        if color in normalized_message:
            preferences["color"] = color
            break

    for fit in FIT_KEYWORDS:
        if fit in normalized_message:
            preferences["fit"] = fit
            break

    return preferences


class FashionAIService:
    """Placeholder for future Gemini Flash image and text understanding."""

    async def analyze_image(self) -> None:
        raise NotImplementedError("Gemini Flash image analysis is not implemented in Phase 0.")

    async def generate_response(self) -> None:
        raise NotImplementedError("AI chat response generation is not implemented in Phase 0.")
