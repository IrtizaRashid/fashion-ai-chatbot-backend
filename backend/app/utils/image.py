from fastapi import UploadFile


async def validate_uploaded_image(image: UploadFile) -> bool:
    """Placeholder for future image validation and preprocessing."""
    return image.content_type is not None and image.content_type.startswith("image/")
