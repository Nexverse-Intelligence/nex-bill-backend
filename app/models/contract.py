# Standard library

# Third-party
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)

# Local
from app.enums import ContractStatus
from app.models import BaseModel


class Contract(BaseModel):
    """
    Represents a recurring billing contract with a
    client. Controls invoice auto-generation schedule.
    """

    __tablename__ = "contracts"

    client_id = Column(
        Integer,
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    billing_cycle = Column(
        String(20),
        nullable=False,
        default="MONTHLY",  # MONTHLY | QUARTERLY | ANNUAL
    )
    auto_renew = Column(Boolean, nullable=False, default=False)
    status = Column(
        Enum(ContractStatus),
        nullable=False,
        default=ContractStatus.ACTIVE,
    )
    deleted_at = Column(DateTime, nullable=True)
