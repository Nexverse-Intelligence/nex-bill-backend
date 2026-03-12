# Standard library
import enum


class InvoiceStatus(enum.StrEnum):
    """
    Lifecycle states for an Invoice.
    Inherits from str for JSON serialization support.
    """

    DRAFT = "DRAFT"
    SENT = "SENT"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    VOID = "VOID"
