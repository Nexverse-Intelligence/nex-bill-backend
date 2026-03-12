# Standard library
from datetime import datetime

# Third-party
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)

# Local
from app.models import BaseModel


class Payment(BaseModel):
    """
    Records a payment transaction against an Invoice.
    """

    __tablename__ = "payments"

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        nullable=False,
        index=True,
    )
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(
        String(50),
        nullable=False,
        default="manual",
    )
    provider_ref = Column(String(255), nullable=True)
    paid_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
