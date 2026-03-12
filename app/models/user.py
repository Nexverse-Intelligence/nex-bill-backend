# Standard library

# Third-party
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
)

# Local
from app.models import BaseModel


class User(BaseModel):
    """
    Represents an authenticated application user.
    Roles: 'admin' or 'staff'.
    """

    __tablename__ = "users"

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(20),
        nullable=False,
        default="staff",
    )
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime, nullable=True)
