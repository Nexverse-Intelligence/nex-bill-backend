# Standard library

# Third-party
from pydantic import BaseModel, Field


class BrandSettingsUpdate(BaseModel):
    """
    Schema for updating workspace branding.
    All fields are optional — only provided fields
    will be updated (PATCH semantics).
    """

    brand_name: str | None = Field(default=None, max_length=100)
    primary_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    accent_color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    invoice_prefix: str | None = Field(default=None, max_length=10)
    footer_text: str | None = Field(default=None, max_length=500)
    support_email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)


class BrandSettingsResponse(BaseModel):
    """Schema for brand settings API response."""

    brand_name: str
    logo_url: str | None
    primary_color: str
    accent_color: str
    invoice_prefix: str
    footer_text: str | None
    support_email: str | None
    website: str | None

    model_config = {"from_attributes": True}
