# Standard library
from datetime import datetime

# Third-party
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

# Local
from app.enums import InvoiceStatus
from app.models import BaseModel


class Invoice(BaseModel):
    """
    Represents a billing invoice sent to a client.
    Tracks payment progress and lifecycle status.
    """

    __tablename__ = "invoices"

    client_id = Column(
        Integer,
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )
    contract_id = Column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=True,
        index=True,
    )
    invoice_number = Column(String(50), unique=True, nullable=False)
    status = Column(
        Enum(InvoiceStatus),
        nullable=False,
        default=InvoiceStatus.DRAFT,
    )
    currency = Column(String(3), nullable=False, default="USD")
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    amount_paid = Column(Numeric(12, 2), nullable=False, default=0)
    due_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )


class InvoiceItem(BaseModel):
    """
    A single line item on an Invoice.
    """

    __tablename__ = "invoice_items"

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        nullable=False,
        index=True,
    )
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)
    discount = Column(Numeric(5, 2), nullable=False, default=0)

    invoice = relationship("Invoice", back_populates="items")


class WebhookEvent(BaseModel):
    """
    Idempotency guard for incoming webhook events.
    Prevents duplicate processing.
    (No internal_id needed — internal-only table.)
    """

    __tablename__ = "webhook_events"

    event_id = Column(String(255), unique=True, nullable=False)
    provider = Column(String(50), nullable=False, default="stripe")
    processed_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class AuditLog(BaseModel):
    """
    Immutable record of significant domain events.
    (No internal_id needed — internal-only table.)
    """

    __tablename__ = "audit_logs"

    entity = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    changed_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
