# Standard library
import uuid
from datetime import date

# Third-party
from pydantic import BaseModel, Field

# Local
from app.enums import ContractStatus


class ContractCreate(BaseModel):
    """Schema for creating a new contract."""

    client_id: int
    start_date: date
    end_date: date | None = None
    billing_cycle: str = Field(
        default="MONTHLY",
        description="MONTHLY | QUARTERLY | ANNUAL",
    )
    auto_renew: bool = False


class ContractUpdate(BaseModel):
    """Schema for updating a contract (PATCH style)."""

    end_date: date | None = None
    billing_cycle: str | None = None
    auto_renew: bool | None = None


class ContractResponse(BaseModel):
    """
    Schema for returning a contract.

    ``internal_id`` is the UUID7 value the frontend
    should use as the canonical identifier.
    """

    internal_id: uuid.UUID
    start_date: date
    end_date: date | None
    billing_cycle: str
    auto_renew: bool
    status: ContractStatus

    model_config = {"from_attributes": True}
