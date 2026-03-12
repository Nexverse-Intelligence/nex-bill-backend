# Standard library
import uuid
from datetime import datetime

# Third-party
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Local
from app.infrastructure.database import Base


def _new_uuid7() -> uuid.UUID:
    """Generate a new UUID version 7 value."""
    return uuid.uuid7()


class BaseModel(Base):
    """
    Abstract base model for all domain entities.
    Provides common columns across all tables.

    - `id`: Internal integer primary key for fast joins.
    - `internal_id`: Public UUIDv7 for API exposure.
    - `created_at`: Timestamp of creation.
    - `updated_at`: Timestamp of last update.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    internal_id = Column(
        PG_UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=_new_uuid7,
        index=True,
        comment="Public UUID v7 identifier for API consumers.",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
