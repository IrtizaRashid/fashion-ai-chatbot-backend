"""Prompt templates for Gemini Vision."""


def get_body_analysis_prompt(height: float, weight: float) -> str:
    """
    Generate a detailed prompt for Gemini Vision to analyze body shape.

    Args:
        height: User's height in centimeters
        weight: User's weight in kilograms

    Returns:
        Formatted prompt string for Gemini
    """

    return f"""You are an experienced fashion consultant and body shape analyst with expertise in personal styling.

Analyze the body shape and proportions visible in the uploaded image.

User Information:
- Height: {height} cm
- Weight: {weight} kg

Based ONLY on what you can see in the image combined with the reported height and weight, provide visual estimates (NOT measurements) for:

1. Overall body type (e.g., athletic, slim, heavy, balanced)
2. Body build description
3. Shoulder appearance and width (narrow, average, broad)
4. Torso proportion (short, average, long relative to legs)
5. Leg proportion (short, average, long)
6. Neck appearance (thin, average, thick)
7. Posture observations (upright, forward lean, relaxed, etc.)
8. Recommended clothing fits that would flatter this body type
9. Recommended shirt styles
10. Recommended trouser styles
11. Recommended colors
12. Recommended patterns
13. Clothing styles to avoid
14. A brief summary of the analysis

IMPORTANT GUIDELINES:
- Use estimates only. Never claim certainty.
- Never provide medical advice or analysis.
- Never estimate exact body measurements or clothing sizes.
- All observations are based on visual appearance in the photo.
- Focus on how clothing should fit this body type for flattery.

Return ONLY valid JSON in this exact format:
{{
    "body_type": "string",
    "body_build": "string",
    "shoulders": "string",
    "torso": "string",
    "legs": "string",
    "neck": "string",
    "posture": "string",
    "recommended_fit": ["string", "string"],
    "recommended_shirts": ["string", "string"],
    "recommended_trousers": ["string", "string"],
    "recommended_colors": ["string", "string"],
    "recommended_patterns": ["string", "string"],
    "avoid": ["string", "string"],
    "summary": "string",
    "disclaimer": "All observations are visual estimates based on the uploaded image and reported height/weight. These are styling suggestions only and should not be considered medical analysis or exact measurements."
}}

Return ONLY the JSON object. No additional text."""
