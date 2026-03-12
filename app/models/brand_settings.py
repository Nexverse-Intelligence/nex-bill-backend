# Third-party
from sqlalchemy import Column, String, Text

# Local
from app.models import BaseModel


class BrandSettings(BaseModel):
    """
    Stores workspace-level branding configuration.
    Falls back to NexBill defaults when a field is
    null or not yet customised.
    """

    __tablename__ = "brand_settings"

    brand_name = Column(
        String(100),
        nullable=False,
        default="NexBill",
    )
    logo_url = Column(Text, nullable=True)
    primary_color = Column(
        String(7),
        nullable=False,
        default="#1A56DB",
    )
    accent_color = Column(
        String(7),
        nullable=False,
        default="#7E3AF2",
    )
    invoice_prefix = Column(
        String(10),
        nullable=False,
        default="INV",
    )
    footer_text = Column(Text, nullable=True)
    support_email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
