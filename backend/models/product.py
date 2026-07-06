from pydantic import BaseModel, Field, HttpUrl


class Product(BaseModel):
    brand: str
    title: str
    price: int | None = None
    currency: str = "PKR"
    color: str | None = None
    colors: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    material: str | None = None
    image_url: HttpUrl | str | None = None
    product_url: HttpUrl | str | None = None
    available: bool | None = None
    relevance_score: float = 0


class ProductSearchRequest(BaseModel):
    recommended_fit: list[str] = Field(default_factory=list)
    recommended_shirts: list[str] = Field(default_factory=list)
    recommended_colors: list[str] = Field(default_factory=list)
    budget: int | None = None


class ProductSearchResponse(BaseModel):
    products: list[Product]
