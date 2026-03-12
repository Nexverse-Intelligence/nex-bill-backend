# Standard library
from datetime import date, datetime
from decimal import Decimal

# Third-party
from sqlalchemy.orm import Session

# Local
from app.enums.invoice_status import InvoiceStatus
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.user import User
from app.repositories.payment_repository import (
    PaymentRepository,
)


def create_invoice_and_payment(
    db: Session,
    client_id: int,
    user_id: int,
    amount: Decimal,
) -> tuple[Invoice, Payment]:
    """Helper: create Invoice + Payment."""
    inv = Invoice(
        client_id=client_id,
        invoice_number=(f"INV-P{abs(hash(str(amount)))%100000:05d}"),
        status=InvoiceStatus.PAID,
        currency="USD",
        total_amount=amount,
        amount_paid=amount,
        due_date=date.today(),
        created_by=user_id,
    )
    db.add(inv)
    db.flush()

    pmt = Payment(
        invoice_id=inv.id,
        amount=amount,
        method="stripe",
        paid_at=datetime.utcnow(),
    )
    db.add(pmt)
    db.flush()
    return inv, pmt


class TestPaymentRepository:
    """Integration tests for PaymentRepository."""

    def test_get_by_invoice(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        get_by_invoice should return all payments for
        the requested invoice ID.
        """
        inv, pmt = create_invoice_and_payment(
            db,
            test_client.id,
            test_user.id,
            Decimal("150"),
        )
        repo = PaymentRepository(db)
        results = repo.get_by_invoice(inv.id)

        assert len(results) == 1
        assert results[0].invoice_id == inv.id
        assert results[0].amount == Decimal("150")

    def test_get_by_invoice_empty(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        get_by_invoice should return [] for an invoice
        with no payments.
        """
        inv = Invoice(
            client_id=test_client.id,
            invoice_number="INV-NOPAY",
            status=InvoiceStatus.SENT,
            currency="USD",
            total_amount=Decimal("50"),
            amount_paid=Decimal("0"),
            due_date=date.today(),
            created_by=test_user.id,
        )
        db.add(inv)
        db.flush()
        repo = PaymentRepository(db)
        results = repo.get_by_invoice(inv.id)
        assert results == []
