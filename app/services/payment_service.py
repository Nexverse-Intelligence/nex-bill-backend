# Standard library

# Third-party
from sqlalchemy.orm import Session

# Local
from app.exceptions import InvoiceNotFoundError
from app.models import Payment
from app.repositories import (
    InvoiceRepository,
    PaymentRepository,
)


class PaymentService:
    """
    Handles payment recording and listing for invoices.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.invoice_repo = InvoiceRepository(db)

    def get_payments_for_invoice(self, invoice_id: int) -> list[Payment]:
        """
        Fetch all payments for a given invoice.

        Args:
            invoice_id: Invoice primary key.

        Returns:
            List of Payment records.

        Raises:
            InvoiceNotFoundError: Invoice not found.
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found.")
        return self.payment_repo.get_by_invoice(invoice_id)
