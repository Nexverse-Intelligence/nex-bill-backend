"""
Domain exceptions for the NexBill application.

These are raised by the service layer and caught by
the API layer, which converts them to HTTP responses.
"""


class InvoiceNotFoundError(Exception):
    """Raised when an invoice cannot be located."""

    pass


class InvalidPaymentError(ValueError):
    """
    Raised when a payment amount is invalid relative
    to the invoice total or current balance.
    """

    pass


class ContractNotFoundError(Exception):
    """Raised when a contract cannot be located."""

    pass


class ContractExpiredError(Exception):
    """Raised when acting on an expired contract."""

    pass


class ClientNotFoundError(Exception):
    """Raised when a client cannot be located."""

    pass


class DuplicateWebhookError(Exception):
    """Raised when a webhook event is redelivered."""

    pass


class UnauthorizedError(Exception):
    """Raised when authentication fails."""

    pass


class ForbiddenError(Exception):
    """Raised when the user lacks required role."""

    pass
