"""Natural language parser for follow-up filtering requests."""

from __future__ import annotations

import json
import logging
import re

import google.generativeai as genai

from conversation.schemas import FilterCriteria
from core.config import settings

logger = logging.getLogger(__name__)


class FollowUpParser:
    """Parses chat follow-ups into filter criteria using Gemini with heuristic fallback."""

    async def parse(self, message: str) -> FilterCriteria:
        try:
            criteria = await self._parse_with_gemini(message)
            if criteria:
                return criteria
        except Exception as exc:
            logger.info("Gemini follow-up parsing fallback used: %s", exc)
        return self._parse_heuristic(message)

    async def _parse_with_gemini(self, message: str) -> FilterCriteria | None:
        if not settings.GEMINI_API_KEY:
            return None

        prompt = f"""
You convert fashion shopping follow-up messages into JSON filters.
Return JSON only. Use null for missing values.

Supported keys:
brand, exclude_brand, color, material, max_price, min_price, fit, pattern,
category, available, occasion, sort, reset_filters.

Examples:
"Show only blue shirts" -> {{"color":"Blue","category":"Shirt"}}
"Only cotton" -> {{"material":"Cotton"}}
"Remove Outfitters" -> {{"exclude_brand":"Outfitters"}}
"Under PKR 4000" -> {{"max_price":4000}}
"Show formal shirts" -> {{"category":"Formal Shirt","occasion":"Formal"}}
"Show more expensive options" -> {{"sort":"expensive"}}
"Start again" -> {{"reset_filters":true}}

Message:
{message}
"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        payload = self._extract_json(text)
        return FilterCriteria.model_validate(payload)

    def _parse_heuristic(self, message: str) -> FilterCriteria:
        text = message.lower()
        criteria = FilterCriteria()

        if any(term in text for term in ["reset", "start again", "show all", "all products", "clear filter"]):
            criteria.reset_filters = True

        brands = {
            "outfitters": "Outfitters",
            "breakout": "Breakout",
            "j.": "J.",
            "junaid": "J.",
            "jamshed": "J.",
        }
        for token, brand in brands.items():
            if token in text:
                if any(term in text for term in ["remove", "exclude", "without", "not "]):
                    criteria.exclude_brand = brand
                else:
                    criteria.brand = brand

        colors = ["black", "white", "blue", "navy", "green", "olive", "brown", "grey", "gray", "red", "maroon", "beige", "cream"]
        for color in colors:
            if re.search(rf"\b{re.escape(color)}\b", text):
                criteria.color = "Grey" if color == "gray" else color.title()
                break

        materials = ["cotton", "linen", "denim", "polyester", "fleece", "wool", "twill", "jersey"]
        for material in materials:
            if material in text:
                criteria.material = material.title()
                break

        price = self._extract_price(text)
        if price is not None:
            if any(term in text for term in ["above", "over", "more than", "expensive"]):
                criteria.min_price = price
            else:
                criteria.max_price = price

        if any(term in text for term in ["cheap", "cheaper", "low price", "budget"]):
            criteria.sort = "cheap"
        if any(term in text for term in ["expensive", "premium", "higher price"]):
            criteria.sort = "expensive"

        if "slim" in text:
            criteria.fit = "Slim Fit"
        elif "regular" in text:
            criteria.fit = "Regular Fit"
        elif "loose" in text or "oversized" in text:
            criteria.fit = "Oversized"

        if "stripe" in text:
            criteria.pattern = "Stripe"
        elif "solid" in text or "plain" in text:
            criteria.pattern = "Solid"
        elif "check" in text:
            criteria.pattern = "Check"

        if any(term in text for term in ["formal", "office", "smart"]):
            criteria.occasion = "Formal"
        elif any(term in text for term in ["casual", "daily", "college"]):
            criteria.occasion = "Casual"
        elif any(term in text for term in ["party", "wedding"]):
            criteria.occasion = "Occasion"

        if any(term in text for term in ["formal shirt", "office shirt"]):
            criteria.category = "Formal Shirt"
        elif any(term in text for term in ["polo"]):
            criteria.category = "Polo Shirt"
        elif any(term in text for term in ["t-shirt", "tshirt", "tee"]):
            criteria.category = "T-Shirt"
        elif any(term in text for term in ["shirt", "shirts"]):
            criteria.category = "Shirt"
        elif any(term in text for term in ["pant", "trouser", "jean", "chino"]):
            criteria.category = "Trouser"

        if any(term in text for term in ["available", "in stock"]):
            criteria.available = True

        return criteria

    @staticmethod
    def _extract_price(text: str) -> int | None:
        match = re.search(r"\b(\d{3,6})\b", text.replace(",", ""))
        return int(match.group(1)) if match else None

    @staticmethod
    def _extract_json(text: str) -> dict:
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.strip("`")
            if clean.lower().startswith("json"):
                clean = clean[4:].strip()
        start = clean.find("{")
        end = clean.rfind("}")
        if start == -1 or end == -1:
            return {}
        return json.loads(clean[start : end + 1])
