from typing import Literal, Optional

from pydantic import BaseModel, Field


class PaymentQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    sort_by: Literal["created_at", "updated_at"] = "created_at"
    sort_order: Literal[1, -1] = -1
    search: Optional[str] = Field(default=None, max_length=200)


class PaymentCreateBodySchema(BaseModel):
    pass


class PaymentUpdateBodySchema(BaseModel):
    pass
