# Standard library

# Third-party
from sqlalchemy.orm import Session

# Local
from app.models import Payment
from app.repositories import (
    BaseRepository,
)


class PaymentRepository(BaseRepository[Payment]):
    """
    Data access layer for Payment records.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Payment, db)

    def get_by_invoice(self, invoice_id: int) -> list[Payment]:
        """
        Fetch all payments for a given invoice.

        Args:
            invoice_id: Invoice primary key.

        Returns:
            Payments ordered by paid_at desc.
        """
        return (
            self.db.query(Payment)
            .filter(Payment.invoice_id == invoice_id)
            .order_by(Payment.paid_at.desc())
            .all()
        )
