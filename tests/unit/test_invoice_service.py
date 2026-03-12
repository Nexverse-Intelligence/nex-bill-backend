# Standard library
from datetime import date
from decimal import Decimal
from itertools import count

# Third-party
import pytest
from sqlalchemy.orm import Session

# Local
from app.enums.invoice_status import InvoiceStatus
from app.exceptions import (
    ClientNotFoundError,
    InvalidPaymentError,
    InvoiceNotFoundError,
)
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.invoice_schema import (
    InvoiceCreate,
    InvoiceItemCreate,
)
from app.services.invoice_service import InvoiceService

_inv_counter = count(1)


def make_invoice(
    db: Session,
    client_id: int,
    user_id: int,
    total: Decimal = Decimal("100.00"),
    status: InvoiceStatus = InvoiceStatus.SENT,
) -> Invoice:
    """Helper: create and flush an Invoice."""
    from app.models.invoice import Invoice

    inv = Invoice(
        client_id=client_id,
        invoice_number=f"INV-{next(_inv_counter):06d}",
        status=status,
        currency="USD",
        total_amount=total,
        amount_paid=Decimal("0"),
        due_date=date.today(),
        created_by=user_id,
    )
    db.add(inv)
    db.flush()
    return inv


class TestInvoiceServiceCreate:
    """Unit tests for InvoiceService.create_invoice."""

    def test_create_invoice_ok(
        self, db: Session, test_client: Client, test_user: User
    ) -> None:
        """
        Creating an invoice with one line item should
        return a flushed Invoice with a positive total.
        """
        service = InvoiceService(db)
        payload = InvoiceCreate(
            client_id=test_client.id,
            due_date=date.today(),
            currency="USD",
            items=[
                InvoiceItemCreate(
                    description="Service fee",
                    quantity=Decimal("2"),
                    unit_price=Decimal("50"),
                )
            ],
        )
        invoice = service.create_invoice(payload, created_by=test_user.id)
        assert invoice.id is not None
        assert invoice.total_amount == Decimal("100")
        assert invoice.status == InvoiceStatus.DRAFT

    def test_create_invoice_client_not_found(
        self, db: Session, test_user: User
    ) -> None:
        """
        Creating an invoice for a non-existent client
        should raise ClientNotFoundError.
        """
        service = InvoiceService(db)
        payload = InvoiceCreate(
            client_id=999999,
            due_date=date.today(),
            currency="USD",
            items=[
                InvoiceItemCreate(
                    description="X",
                    quantity=Decimal("1"),
                    unit_price=Decimal("10"),
                )
            ],
        )
        with pytest.raises(ClientNotFoundError):
            service.create_invoice(payload, created_by=test_user.id)


class TestInvoiceServiceRecordPayment:
    """Unit tests for InvoiceService.record_payment."""

    def test_record_full_payment(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        Recording a payment equal to the total should
        transition the invoice to PAID.
        """
        invoice = make_invoice(
            db,
            test_client.id,
            test_user.id,
            total=Decimal("200"),
        )
        service = InvoiceService(db)
        updated = service.record_payment(
            invoice_id=invoice.id,
            amount=Decimal("200"),
        )
        assert updated.status == InvoiceStatus.PAID
        assert updated.amount_paid == Decimal("200")

    def test_record_partial_payment(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        Recording a partial payment should transition
        the invoice to PARTIALLY_PAID.
        """
        invoice = make_invoice(
            db,
            test_client.id,
            test_user.id,
            total=Decimal("200"),
        )
        service = InvoiceService(db)
        updated = service.record_payment(
            invoice_id=invoice.id,
            amount=Decimal("100"),
        )
        assert updated.status == (InvoiceStatus.PARTIALLY_PAID)

    def test_payment_exceeds_total(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        Recording a payment exceeding the invoice total
        should raise InvalidPaymentError.
        """
        invoice = make_invoice(
            db,
            test_client.id,
            test_user.id,
            total=Decimal("100"),
        )
        service = InvoiceService(db)
        with pytest.raises(InvalidPaymentError):
            service.record_payment(
                invoice_id=invoice.id,
                amount=Decimal("200"),
            )

    def test_payment_invoice_not_found(self, db: Session) -> None:
        """
        Recording a payment for a missing invoice
        should raise InvoiceNotFoundError.
        """
        service = InvoiceService(db)
        with pytest.raises(InvoiceNotFoundError):
            service.record_payment(
                invoice_id=999999,
                amount=Decimal("10"),
            )


class TestInvoiceServiceBatch:
    """Unit tests for process_invoice_batch."""

    def test_batch_success(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        process_invoice_batch should report success
        for valid invoice IDs.
        """
        inv1 = make_invoice(db, test_client.id, test_user.id)
        inv2 = make_invoice(db, test_client.id, test_user.id)
        service = InvoiceService(db)
        results = service.process_invoice_batch([inv1.id, inv2.id])
        assert len(results["success"]) == 2
        assert results["failed"] == []

    def test_batch_partial_failure(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        process_invoice_batch should add missing IDs
        to 'failed' without rolling back successful
        ones.
        """
        inv = make_invoice(db, test_client.id, test_user.id)
        service = InvoiceService(db)
        results = service.process_invoice_batch([inv.id, 999999])
        assert inv.id in results["success"]
        assert 999999 in results["failed"]
