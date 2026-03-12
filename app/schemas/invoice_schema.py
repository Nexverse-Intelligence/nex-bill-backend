# Standard library
import uuid
from datetime import date, datetime
from decimal import Decimal

# Third-party
from pydantic import BaseModel, Field

# Local
from app.enums import InvoiceStatus


class InvoiceItemCreate(BaseModel):
    """Schema for a single invoice line item."""

    description: str
    quantity: Decimal = Field(default=Decimal("1"))
    unit_price: Decimal
    tax_rate: Decimal = Field(default=Decimal("0"))
    discount: Decimal = Field(default=Decimal("0"))


class InvoiceItemResponse(BaseModel):
    """Schema for returning an invoice line item."""

    internal_id: uuid.UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    discount: Decimal

    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    """Schema for creating a new invoice."""

    client_id: int
    contract_id: int | None = None
    due_date: date
    currency: str = Field(default="USD", max_length=3)
    notes: str | None = None
    items: list[InvoiceItemCreate] = Field(min_length=1)


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice (PATCH style)."""

    due_date: date | None = None
    notes: str | None = None
    status: InvoiceStatus | None = None


class InvoiceResponse(BaseModel):
    """
    Schema for returning an invoice.

    ``internal_id`` is the UUID7 value the frontend
    should use as the canonical identifier.
    ``id`` is omitted — internal DB key only.
    """

    internal_id: uuid.UUID
    invoice_number: str
    status: InvoiceStatus
    currency: str
    total_amount: Decimal
    amount_paid: Decimal
    due_date: date
    notes: str | None
    items: list[InvoiceItemResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceListResponse(BaseModel):
    """Schema for paginated invoice list."""

    items: list[InvoiceResponse]
    total: int
    skip: int
    limit: int
