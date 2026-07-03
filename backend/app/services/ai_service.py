from typing import Any

from fastapi import UploadFile


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


async def analyze_image(
    image: UploadFile,
    height: int | None = None,
    weight: int | None = None,
) -> dict[str, Any]:
    """Mock image analysis layer; replace with Gemini Flash later."""
    body_type = _estimate_body_type(height=height, weight=weight)
    confidence = _estimate_confidence(height=height, weight=weight)
    recommended_size = _recommend_size(body_type=body_type, height=height, weight=weight)

    return {
        "body_type": body_type,
        "confidence": confidence,
        "recommended_size": recommended_size,
        "recommendations": _build_recommendations(body_type, recommended_size),
    }


def generate_fashion_response(session_data: Any, message: str | None) -> dict[str, Any]:
    preferences = session_data.preferences
    color = preferences.get("color")
    fit = preferences.get("fit")
    budget = preferences.get("budget")
    body_type = session_data.body_type or "your current profile"
    recommended_size = session_data.recommended_size or "standard sizing"

    response_parts = [
        f"I will use your {body_type} profile",
        f"and start with {recommended_size}",
    ]

    if color:
        response_parts.append(f"with {color} options")
    if fit:
        response_parts.append(f"in a {fit} fit")
    if budget:
        response_parts.append(f"around your {budget} budget")

    return {
        "message": " ".join(response_parts) + ".",
        "recommendations": _build_recommendations(
            body_type=session_data.body_type or "athletic",
            recommended_size=session_data.recommended_size or "M",
            color=color,
            fit=fit,
        ),
    }


class FashionAIService:
    """Future Gemini Flash adapter for image and chat intelligence."""

    async def analyze_image(
        self,
        image: UploadFile,
        height: int | None = None,
        weight: int | None = None,
    ) -> dict[str, Any]:
        return await analyze_image(image=image, height=height, weight=weight)

    async def generate_response(self, session_data: Any, message: str | None) -> dict[str, Any]:
        return generate_fashion_response(session_data=session_data, message=message)


def _estimate_body_type(height: int | None, weight: int | None) -> str:
    if height is None or weight is None:
        return "athletic"

    height_m = height / 100
    bmi = weight / (height_m * height_m)

    if bmi < 20:
        return "slim"
    if bmi > 27:
        return "heavy"
    return "athletic"


def _estimate_confidence(height: int | None, weight: int | None) -> float:
    if height is not None and weight is not None:
        return 0.87
    if height is not None or weight is not None:
        return 0.72
    return 0.64


def _recommend_size(body_type: str, height: int | None, weight: int | None) -> str:
    if weight is None:
        return "M"

    if body_type == "slim":
        return "S" if weight < 60 else "M"
    if body_type == "heavy":
        return "XL" if weight >= 90 else "L"
    if height is not None and height >= 180:
        return "L"
    return "M"


def _build_recommendations(
    body_type: str,
    recommended_size: str,
    color: str | None = None,
    fit: str | None = None,
) -> list[str]:
    color_text = f"{color} " if color else ""
    fit_text = fit or _default_fit_for_body_type(body_type)

    return [
        f"{color_text}{fit_text} shirt in size {recommended_size}".strip(),
        f"Structured jacket or overshirt in size {recommended_size}",
        "Mid-rise trousers with clean vertical lines",
    ]


def _default_fit_for_body_type(body_type: str) -> str:
    if body_type == "slim":
        return "regular"
    if body_type == "heavy":
        return "relaxed"
    return "tailored"
