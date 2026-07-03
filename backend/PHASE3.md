# Phase 3: Body Analysis Module

## Overview

Phase 3 implements a production-ready body analysis module that uses Google's Gemini 2.5 Flash Vision API to analyze body shapes and proportions from uploaded images.

## Architecture

```
backend/
├── ai/
│   ├── __init__.py           # Module exports
│   ├── body_analyzer.py      # Main analysis logic
│   ├── gemini_client.py      # Gemini API client
│   ├── prompts.py            # Prompt templates
│   └── schemas.py            # Pydantic models
├── api/
│   ├── __init__.py           # Route exports
│   └── analyze.py            # FastAPI endpoints
├── core/
│   └── config.py             # Configuration & env vars
├── main.py                   # FastAPI application
└── requirements-phase3.txt   # Dependencies
```

## API Endpoint

### POST /analyze-body

Analyzes body shape and proportions from an uploaded image.

**Request:**
```
POST /analyze-body
Content-Type: multipart/form-data

image: <image-file> (JPEG, PNG, or WEBP)
height: <float> (cm)
weight: <float> (kg)
```

**Response:**
```json
{
  "body_type": "Athletic",
  "body_build": "Balanced muscular build",
  "shoulders": "Moderately broad shoulders",
  "torso": "Proportionate torso with defined waist",
  "legs": "Well-proportioned legs",
  "neck": "Average neck width",
  "posture": "Upright posture observed",
  "recommended_fit": ["Slim fit", "Tailored"],
  "recommended_shirts": ["Oxford shirts", "Crew neck t-shirts"],
  "recommended_trousers": ["Slim chinos", "Dress pants"],
  "recommended_colors": ["Navy", "Black", "Olive"],
  "recommended_patterns": ["Solid colors", "Subtle patterns"],
  "avoid": ["Oversized fits", "Baggy styles"],
  "summary": "Based on your athletic build...",
  "disclaimer": "All observations are visual estimates..."
}
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements-phase3.txt
```

### 2. Configure Environment

```bash
# Copy example to .env
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_actual_api_key
```

### 3. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "service": "AI Fashion Stylist - Body Analysis"
}
```

## Testing the Endpoint

### Using cURL

```bash
curl -X POST http://localhost:8000/analyze-body \
  -F "image=@/path/to/image.jpg" \
  -F "height=180" \
  -F "weight=75"
```

### Using Python

```python
import requests

with open("image.jpg", "rb") as f:
    files = {"image": f}
    data = {"height": 180, "weight": 75}
    
    response = requests.post(
        "http://localhost:8000/analyze-body",
        files=files,
        data=data
    )
    
    print(response.json())
```

### Using JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append("image", imageFile);
formData.append("height", 180);
formData.append("weight", 75);

const response = await fetch("http://localhost:8000/analyze-body", {
  method: "POST",
  body: formData,
});

const result = await response.json();
console.log(result);
```

## Key Features

### 1. Modular Architecture

- **Gemini Client**: Isolated API client for easy testing and mocking
- **Prompts**: Separate prompt management for easy customization
- **Schemas**: Pydantic models for request/response validation
- **Analyzer**: Core logic that orchestrates the analysis

### 2. Production-Ready Error Handling

- Image validation (type, size)
- Input validation (height, weight ranges)
- JSON parsing error handling
- Detailed HTTP error responses
- Comprehensive logging

### 3. Type Safety

- Full type hints throughout
- Pydantic validation on all inputs/outputs
- IDE autocomplete support

### 4. Security

- Environment variables for API keys (never hardcoded)
- CORS configuration
- File size limits
- File type validation
- Input range validation

## Response Schema Details

| Field | Type | Description |
|-------|------|-------------|
| body_type | string | Overall body type estimate |
| body_build | string | Detailed build description |
| shoulders | string | Shoulder appearance analysis |
| torso | string | Torso proportion observations |
| legs | string | Leg proportion observations |
| neck | string | Neck appearance analysis |
| posture | string | Posture observations |
| recommended_fit | array | List of flattering clothing fits |
| recommended_shirts | array | Recommended shirt styles |
| recommended_trousers | array | Recommended trouser styles |
| recommended_colors | array | Flattering colors |
| recommended_patterns | array | Recommended patterns |
| avoid | array | Styles to avoid |
| summary | string | Overall analysis summary |
| disclaimer | string | Important disclaimer about estimates |

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Height must be between 100cm and 250cm"
}
```

### 413 Payload Too Large
```json
{
  "detail": "Image file too large. Maximum size: 10MB"
}
```

### 415 Unsupported Media Type
```json
{
  "detail": "Unsupported image type. Allowed: image/jpeg, image/png, image/webp"
}
```

### 500 Server Error
```json
{
  "detail": "Failed to analyze body. Please try again."
}
```

## Validation Rules

### Height
- Minimum: 100 cm
- Maximum: 250 cm
- Required: Yes

### Weight
- Minimum: 30 kg
- Maximum: 300 kg
- Required: Yes

### Image
- Formats: JPEG, PNG, WEBP
- Maximum size: 10 MB
- Required: Yes

## Important Notes

1. **Visual Estimates Only**: All observations are estimates based on the uploaded image and reported measurements. Not medical analysis.

2. **No Certainty Claims**: The model uses cautious language and never claims absolute certainty.

3. **No Medical Advice**: The module is designed for fashion styling only.

4. **No Exact Measurements**: Never estimates exact body measurements or clothing sizes.

5. **Disclaimer Included**: Every response includes a disclaimer explaining the limitations.

## Future Integration

This module is designed to be easily imported by Phase 4 for:
- Clothing recommendations
- Size predictions
- Product matching

```python
from ai import analyze_body, BodyAnalysisResponse

# Import and use directly
analysis = await analyze_body(image_data, height, weight)
recommendations = get_recommendations(analysis)
```

## Logging

All operations are logged with appropriate levels:
- **INFO**: Normal operations
- **ERROR**: Input validation failures, API errors
- **DEBUG**: Detailed operation flow (when enabled)

Access logs via stdout when running with uvicorn.

## Performance

- Image analysis: ~5-10 seconds per request (Gemini API latency)
- No caching (each request is fresh analysis)
- Concurrent request handling via FastAPI

## Development

### Adding New Analysis Fields

1. Update `BodyAnalysisResponse` in `schemas.py`
2. Update prompt in `prompts.py`
3. Update Gemini response parsing in `body_analyzer.py`

### Changing Gemini Model

Update `settings.GEMINI_MODEL` in `core/config.py`

### Customizing Prompts

Edit `get_body_analysis_prompt()` in `prompts.py`

## Next Steps (Phase 4)

- Implement clothing recommendations based on body analysis
- Add product searching (Playwright + web scraping)
- Integrate with recommendation engine
- Add caching layer (Redis)
