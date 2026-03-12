# Standard library
from datetime import date
from decimal import Decimal
from itertools import count

# Third-party
import pytest
from sqlalchemy.orm import Session

# Local
from app.enums.contract_status import ContractStatus
from app.enums.invoice_status import InvoiceStatus
from app.exceptions import (
    ContractExpiredError,
    ContractNotFoundError,
)
from app.models.client import Client
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.user import User
from app.services.contract_service import (
    ContractService,
)

_inv_counter = count(10000)


def make_contract(
    db: Session,
    client_id: int,
    status: ContractStatus = ContractStatus.ACTIVE,
) -> Contract:
    """Helper: create and flush a Contract."""
    c = Contract(
        client_id=client_id,
        start_date=date.today(),
        billing_cycle="MONTHLY",
        auto_renew=False,
        status=status,
    )
    db.add(c)
    db.flush()
    return c


def make_invoice(
    db: Session,
    client_id: int,
    contract_id: int,
    user_id: int,
    status: InvoiceStatus = InvoiceStatus.SENT,
) -> Invoice:
    """Helper: create and flush an Invoice."""
    inv = Invoice(
        client_id=client_id,
        contract_id=contract_id,
        invoice_number=f"INV-{next(_inv_counter):06d}",
        status=status,
        currency="USD",
        total_amount=Decimal("100"),
        amount_paid=Decimal("0"),
        due_date=date.today(),
        created_by=user_id,
    )
    db.add(inv)
    db.flush()
    return inv


class TestCancelContract:
    """Unit tests for ContractService.cancel_contract."""

    def test_cancel_voids_pending_invoices(
        self,
        db: Session,
        test_client: Client,
        test_user: User,
    ) -> None:
        """
        Cancelling a contract should set all DRAFT
        and SENT invoices to VOID.
        """
        contract = make_contract(db, test_client.id)
        inv1 = make_invoice(
            db,
            test_client.id,
            contract.id,
            test_user.id,
            status=InvoiceStatus.DRAFT,
        )
        inv2 = make_invoice(
            db,
            test_client.id,
            contract.id,
            test_user.id,
            status=InvoiceStatus.SENT,
        )
        service = ContractService(db)
        result = service.cancel_contract(contract.id)

        assert result.status == ContractStatus.CANCELLED
        db.refresh(inv1)
        db.refresh(inv2)
        assert inv1.status == InvoiceStatus.VOID
        assert inv2.status == InvoiceStatus.VOID

    def test_cancel_already_cancelled(
        self,
        db: Session,
        test_client: Client,
    ) -> None:
        """
        Cancelling an already-cancelled contract
        should raise ContractExpiredError.
        """
        contract = make_contract(
            db,
            test_client.id,
            status=ContractStatus.CANCELLED,
        )
        service = ContractService(db)
        with pytest.raises(ContractExpiredError):
            service.cancel_contract(contract.id)

    def test_cancel_not_found(self, db: Session) -> None:
        """
        Cancelling a non-existent contract should
        raise ContractNotFoundError.
        """
        service = ContractService(db)
        with pytest.raises(ContractNotFoundError):
            service.cancel_contract(999999)
