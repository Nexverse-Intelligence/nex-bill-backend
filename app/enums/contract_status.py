# Standard library
import enum


class ContractStatus(enum.StrEnum):
    """
    Lifecycle states for a Contract.
    Inherits from str for JSON serialization support.
    """

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
