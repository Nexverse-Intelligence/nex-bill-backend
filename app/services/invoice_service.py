# Standard library
import uuid
from datetime import datetime
from decimal import Decimal

# Third-party
from sqlalchemy.orm import Session

# Local
from app.enums import InvoiceStatus
from app.exceptions import (
    ClientNotFoundError,
    InvalidPaymentError,
    InvoiceNotFoundError,
)
from app.models import (
    Invoice,
    InvoiceItem,
    Payment,
    WebhookEvent,
)
from app.repositories import (
    ClientRepository,
    InvoiceRepository,
)
from app.schemas import (
    InvoiceCreate,
    InvoiceUpdate,
)


class InvoiceService:
    """
    Manages invoice lifecycle: creation, status
    transitions, PDF generation, and payment
    reconciliation. Transaction is handled by the
    Unit of Work (get_db dependency).
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.client_repo = ClientRepository(db)

    def _next_invoice_number(self, prefix: str = "INV") -> str:
        """Generate sequential invoice number."""
        count = self.invoice_repo.count_all()
        return f"{prefix}-{count + 1:05d}"

    def get_invoice(self, invoice_id: int) -> Invoice:
        """
        Fetch a single invoice.

        Args:
            invoice_id: Invoice primary key.

        Returns:
            Invoice instance.

        Raises:
            InvoiceNotFoundError: Not found.
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found.")
        return invoice

    def list_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        status: InvoiceStatus | None = None,
    ) -> tuple[list[Invoice], int]:
        """
        Return paginated invoices with total count.

        Args:
            skip: Records to skip.
            limit: Max records to return.
            status: Optional status filter.

        Returns:
            Tuple of (invoice list, total count).
        """
        invoices = self.invoice_repo.get_paginated(
            skip=skip, limit=limit, status=status
        )
        total = self.invoice_repo.count_all()
        return invoices, total

    def create_invoice(
        self,
        payload: InvoiceCreate,
        created_by: int,
        invoice_prefix: str = "INV",
    ) -> Invoice:
        """
        Create an invoice with all its line items.

        No commit/rollback here — the Unit of Work
        in get_db handles transaction boundaries.

        Args:
            payload: Validated invoice creation data.
            created_by: User ID creating the invoice.
            invoice_prefix: Brand prefix for number.

        Returns:
            Flushed Invoice instance with PK assigned.

        Raises:
            ClientNotFoundError: Client not found.
        """
        client = self.client_repo.get_by_id(payload.client_id)
        if not client:
            raise ClientNotFoundError(f"Client {payload.client_id} not found.")

        invoice = Invoice(
            client_id=payload.client_id,
            contract_id=payload.contract_id,
            invoice_number=self._next_invoice_number(invoice_prefix),
            due_date=payload.due_date,
            currency=payload.currency,
            notes=payload.notes,
            status=InvoiceStatus.DRAFT,
            created_by=created_by,
        )
        # flush assigns invoice.id for use below
        self.invoice_repo.create(invoice)

        total = Decimal("0")
        for item_data in payload.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data.model_dump(),
            )
            self.db.add(item)
            line_total = (
                item_data.quantity
                * item_data.unit_price
                * (1 - item_data.discount / 100)
                * (1 + item_data.tax_rate / 100)
            )
            total += line_total

        invoice.total_amount = total
        self.db.flush()

        # No commit — get_db commits after return
        return invoice

    def update_invoice(
        self,
        invoice_id: int,
        payload: InvoiceUpdate,
    ) -> Invoice:
        """
        Apply partial update to an invoice.

        Args:
            invoice_id: Invoice primary key.
            payload: Fields to update.

        Returns:
            Updated Invoice instance.

        Raises:
            InvoiceNotFoundError: Not found.
        """
        invoice = self.get_invoice(invoice_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(invoice, field, value)
        self.db.flush()
        return invoice

    def send_invoice(self, invoice_id: int) -> Invoice:
        """
        Transition a DRAFT invoice to SENT.

        Args:
            invoice_id: Invoice primary key.

        Returns:
            Updated Invoice with SENT status.

        Raises:
            InvoiceNotFoundError: Not found.
        """
        invoice = self.get_invoice(invoice_id)
        if invoice.status != InvoiceStatus.DRAFT:
            raise InvalidPaymentError("Only DRAFT invoices can be sent.")
        invoice.status = InvoiceStatus.SENT
        self.db.flush()
        return invoice

    def record_payment(
        self,
        invoice_id: int,
        amount: Decimal,
        method: str = "manual",
        provider_ref: str | None = None,
    ) -> Invoice:
        """
        Record a payment and update invoice status.

        Args:
            invoice_id: Target invoice primary key.
            amount: Payment amount being recorded.
            method: Payment method identifier.
            provider_ref: Provider transaction ref.

        Returns:
            Updated Invoice instance.

        Raises:
            InvoiceNotFoundError: Invoice not found.
            InvalidPaymentError: Amount exceeds total.
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found.")

        new_paid = invoice.amount_paid + amount
        if new_paid > invoice.total_amount:
            raise InvalidPaymentError("Payment exceeds invoice total.")

        # Step 1: create payment record
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            method=method,
            provider_ref=provider_ref,
            paid_at=datetime.utcnow(),
        )
        self.db.add(payment)
        self.db.flush()

        # Step 2: update invoice balance and status
        invoice.amount_paid = new_paid
        if new_paid >= invoice.total_amount:
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        self.db.flush()

        # get_db commits both steps together
        return invoice

    def process_invoice_batch(
        self,
        invoice_ids: list[int],
    ) -> dict:
        """
        Send a batch of invoices. Each uses a
        savepoint so one failure does not affect
        the others.

        The outer UoW (get_db) commits all successful
        savepoints together at request end.

        Args:
            invoice_ids: List of invoice PKs to send.

        Returns:
            Dict with 'success' and 'failed' ID lists.
        """
        results: dict = {
            "success": [],
            "failed": [],
        }

        for invoice_id in invoice_ids:
            # Savepoint per invoice — nested transaction
            savepoint = self.db.begin_nested()
            try:
                invoice = self.invoice_repo.get_by_id(invoice_id)
                if not invoice:
                    raise InvoiceNotFoundError(
                        f"Invoice {invoice_id} not found."
                    )
                invoice.status = InvoiceStatus.SENT
                self.db.flush()
                savepoint.commit()
                results["success"].append(invoice_id)

            except Exception:
                # Roll back this invoice only
                savepoint.rollback()
                results["failed"].append(invoice_id)

        # Outer UoW (get_db) commits all saved points
        return results

    def handle_stripe_webhook(
        self,
        event_id: str,
        payload: dict,
    ) -> None:
        """
        Process a Stripe webhook event idempotently.

        Skips if event_id already recorded. Otherwise,
        writes the guard record and applies the payment
        in one atomic unit via the UoW.

        Args:
            event_id: Unique Stripe event identifier.
            payload: Full webhook event payload dict.
        """
        existing = (
            self.db.query(WebhookEvent)
            .filter(WebhookEvent.event_id == event_id)
            .first()
        )
        if existing:
            # Already processed — safe to skip
            return

        # Write idempotency guard record
        event_record = WebhookEvent(
            event_id=event_id,
            processed_at=datetime.utcnow(),
        )
        self.db.add(event_record)
        self.db.flush()

        # Apply payment — both flushed, UoW commits
        self._apply_payment_from_webhook(payload)

    def _apply_payment_from_webhook(
        self,
        payload: dict,
    ) -> None:
        """
        Apply a payment from a webhook payload.

        Args:
            payload: Stripe webhook event data.
        """
        intent = payload.get("data", {}).get("object", {})
        invoice_id_str = intent.get("metadata", {}).get("invoice_id")
        amount_received = intent.get("amount_received", 0)

        if not invoice_id_str:
            return

        self.record_payment(
            invoice_id=int(invoice_id_str),
            amount=Decimal(amount_received) / 100,
            method="stripe",
            provider_ref=intent.get("id"),
        )

    def get_invoice_by_uid(self, internal_id: uuid.UUID) -> Invoice:
        """Fetch invoice by UUID7."""
        invoice = self.invoice_repo.get_by_internal_id(internal_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice {internal_id} not found.")
        return invoice

    def update_invoice_by_uid(
        self, internal_id: uuid.UUID, payload: InvoiceUpdate
    ) -> Invoice:
        """Apply partial update to invoice by UUID7."""
        invoice = self.get_invoice_by_uid(internal_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(invoice, field, value)
        self.db.flush()
        return invoice

    def send_invoice_by_uid(self, internal_id: uuid.UUID) -> Invoice:
        """Transition DRAFT invoice to SENT by UUID7."""
        invoice = self.get_invoice_by_uid(internal_id)
        if invoice.status != InvoiceStatus.DRAFT:
            raise InvalidPaymentError("Only DRAFT invoices can be sent.")
        invoice.status = InvoiceStatus.SENT
        self.db.flush()
        return invoice

    def record_payment_by_uid(
        self,
        internal_id: uuid.UUID,
        amount: Decimal,
        method: str = "manual",
        provider_ref: str | None = None,
    ) -> Invoice:
        """Record payment against invoice by UUID7."""
        invoice = self.get_invoice_by_uid(internal_id)
        return self.record_payment(
            invoice_id=invoice.id,
            amount=amount,
            method=method,
            provider_ref=provider_ref,
        )
