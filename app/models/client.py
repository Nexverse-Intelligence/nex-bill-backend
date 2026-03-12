# Standard library

# Third-party
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

# Local
from app.models import BaseModel


class Client(BaseModel):
    """
    Represents a billing client (company or person).
    """

    __tablename__ = "clients"

    name = Column(String(255), nullable=False, index=True)
    tax_id = Column(String(50), nullable=True)
    currency = Column(String(3), nullable=False, default="USD")
    billing_address = Column(Text, nullable=True)
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    deleted_at = Column(DateTime, nullable=True)

    contacts = relationship(
        "Contact",
        back_populates="client",
        cascade="all, delete-orphan",
    )


class Contact(BaseModel):
    """
    A named contact person associated with a Client.
    """

    __tablename__ = "contacts"

    client_id = Column(
        Integer,
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    client = relationship("Client", back_populates="contacts")
