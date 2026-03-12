# Standard library
import uuid

# Third-party
from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    """Schema for creating a client contact."""

    name: str = Field(max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)


class ContactResponse(BaseModel):
    """Schema for returning a contact."""

    internal_id: uuid.UUID
    name: str
    email: str | None
    phone: str | None

    model_config = {"from_attributes": True}


class ClientCreate(BaseModel):
    """Schema for creating a new client."""

    name: str = Field(max_length=255)
    tax_id: str | None = Field(default=None, max_length=50)
    currency: str = Field(default="USD", max_length=3)
    billing_address: str | None = None
    contacts: list[ContactCreate] = Field(default_factory=list)


class ClientUpdate(BaseModel):
    """Schema for updating a client (PATCH style)."""

    name: str | None = Field(default=None, max_length=255)
    tax_id: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, max_length=3)
    billing_address: str | None = None


class ClientResponse(BaseModel):
    """
    Schema for returning a client.

    ``internal_id`` is the UUID7 value the frontend
    should use as the canonical identifier.
    """

    internal_id: uuid.UUID
    name: str
    tax_id: str | None
    currency: str
    billing_address: str | None
    contacts: list[ContactResponse] = []

    model_config = {"from_attributes": True}
