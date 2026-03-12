# Standard library
import uuid
from datetime import datetime
from decimal import Decimal

# Third-party
from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    """Schema for recording a manual payment."""

    amount: Decimal = Field(gt=0)
    method: str = Field(default="manual", max_length=50)
    provider_ref: str | None = Field(default=None, max_length=255)


class PaymentResponse(BaseModel):
    """Schema for returning a payment record."""

    internal_id: uuid.UUID
    amount: Decimal
    method: str
    provider_ref: str | None
    paid_at: datetime

    model_config = {"from_attributes": True}
