# Standard library
from datetime import date
from decimal import Decimal
from itertools import count

# Third-party
from sqlalchemy.orm import Session

from app.enums.invoice_status import InvoiceStatus

# Local
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.user import User
from app.repositories.invoice_repository import (
    InvoiceRepository,
)

_inv_counter = count(20000)


def create_invoice(
    db: Session,
    client_id: int,
    user_id: int,
    status: InvoiceStatus = InvoiceStatus.SENT,
    days_overdue: int = 0,
) -> Invoice:
    """Helper: create a flushed Invoice."""
    from datetime import timedelta

    due = date.today() - timedelta(days=days_overdue)
    inv = Invoice(
        client_id=client_id,
        invoice_number=f"INV-{next(_inv_counter):06d}",
        status=status,
        currency="USD",
        total_amount=Decimal("200"),
        amount_paid=Decimal("0"),
        due_date=due,
        created_by=user_id,
    )
    db.add(inv)
    db.flush()
    return inv


class TestInvoiceRepository:
    """Integration tests for InvoiceRepository."""

    def test_get_by_client(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        get_by_client should return invoices for the
        given client only.
        """
        create_invoice(db, test_client.id, test_user.id)
        repo = InvoiceRepository(db)
        results = repo.get_by_client(test_client.id)

        assert len(results) >= 1
        assert all(r.client_id == test_client.id for r in results)

    def test_get_overdue(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        get_overdue should only return SENT invoices
        with past due dates.
        """
        overdue = create_invoice(
            db,
            test_client.id,
            test_user.id,
            status=InvoiceStatus.SENT,
            days_overdue=5,
        )
        current = create_invoice(
            db,
            test_client.id,
            test_user.id,
            status=InvoiceStatus.SENT,
            days_overdue=0,
        )
        repo = InvoiceRepository(db)
        results = repo.get_overdue()

        overdue_ids = [r.id for r in results]
        assert overdue.id in overdue_ids
        # A due_date of today is NOT overdue
        assert current.id not in overdue_ids
