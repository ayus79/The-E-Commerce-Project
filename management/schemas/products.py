from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ProductsQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    sort_by: Literal["created_at", "updated_at"] = "created_at"
    sort_order: Literal[1, -1] = -1
    search: Optional[str] = Field(default=None, max_length=200)


class ProductsCreateBodySchema(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64, description="Unique product SKU")
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(
        ..., min_length=1, max_length=255, description="URL-friendly unique identifier"
    )
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0, description="Product price, must be >= 0")
    currency: str = Field(..., min_length=3, max_length=3)
    attributes: Optional[dict] = Field(
        default=None, description="Flexible per-category fields"
    )
    is_published: bool = Field(default=False)
    is_active: bool = Field(default=True)

    @field_validator("sku")
    @classmethod
    def sku_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("sku must not contain spaces")
        return v.strip().upper()

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not v.replace("-", "").isalnum():
            raise ValueError("slug must be lowercase alphanumeric with hyphens only")
        return v

    @field_validator("currency")
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        return v.upper()

    model_config = {
        "json_schema_extra": {
            "example": {
                "sku": "SKU-12345",
                "name": "Wireless Keyboard",
                "slug": "wireless-keyboard",
                "description": "A compact wireless keyboard with backlight.",
                "price": 49.99,
                "currency": "USD",
                "attributes": {
                    "brand": "Logitech",
                    "warranty_months": 12,
                    "battery_life_hours": 20,
                    "connectivity": ["bluetooth", "usb-c"],
                },
                "is_published": False,
                "is_active": True,
            }
        }
    }


class ProductsUpdateBodySchema(BaseModel):
    pass
