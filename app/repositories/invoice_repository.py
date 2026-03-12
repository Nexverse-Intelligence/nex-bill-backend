# Standard library
from datetime import date

# Third-party
from sqlalchemy.orm import Session

# Local
from app.enums import InvoiceStatus
from app.models import Invoice
from app.repositories import (
    BaseRepository,
)


class InvoiceRepository(BaseRepository[Invoice]):
    """
    Data access layer for Invoice records.
    Extends BaseRepository with invoice-specific
    query methods.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Invoice, db)

    def get_by_client(self, client_id: int) -> list[Invoice]:
        """
        Fetch all invoices for a given client.

        Args:
            client_id: Client primary key to filter.

        Returns:
            Invoices ordered by creation date desc.
        """
        return (
            self.db.query(Invoice)
            .filter(Invoice.client_id == client_id)
            .order_by(Invoice.created_at.desc())
            .all()
        )

    def get_overdue(self) -> list[Invoice]:
        """
        Fetch all invoices past their due date.

        Returns:
            SENT invoices with due_date before today.
        """
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.status == InvoiceStatus.SENT,
                Invoice.due_date < date.today(),
            )
            .all()
        )

    def get_pending_by_contract(self, contract_id: int) -> list[Invoice]:
        """
        Fetch non-paid invoices for a contract.
        Used when cancelling a contract.

        Args:
            contract_id: Contract primary key.

        Returns:
            DRAFT or SENT invoices for the contract.
        """
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.contract_id == contract_id,
                Invoice.status.in_(
                    [
                        InvoiceStatus.DRAFT,
                        InvoiceStatus.SENT,
                    ]
                ),
            )
            .all()
        )

    def count_all(self) -> int:
        """Return total number of invoices."""
        return self.db.query(Invoice).count()

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        status: InvoiceStatus | None = None,
    ) -> list[Invoice]:
        """
        Fetch invoices with optional status filter.

        Args:
            skip: Records to skip.
            limit: Max records to return.
            status: Optional status filter.

        Returns:
            Paginated list of invoices.
        """
        query = self.db.query(Invoice)
        if status:
            query = query.filter(Invoice.status == status)
        return (
            query.order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
