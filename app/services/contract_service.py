# Standard library
import uuid

# Third-party
from sqlalchemy.orm import Session

# Local
from app.enums import ContractStatus, InvoiceStatus
from app.exceptions import (
    ContractExpiredError,
    ContractNotFoundError,
)
from app.models import AuditLog, Contract
from app.repositories import (
    ContractRepository,
    InvoiceRepository,
)
from app.schemas import (
    ContractCreate,
    ContractUpdate,
)


class ContractService:
    """
    Manages contract lifecycle: creation, updates,
    pause, and cancellation with invoice voiding.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.contract_repo = ContractRepository(db)
        self.invoice_repo = InvoiceRepository(db)

    def list_contracts(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contract]:
        """
        Return a paginated list of contracts.

        Args:
            skip: Records to skip.
            limit: Max records to return.

        Returns:
            List of Contract records.
        """
        return self.contract_repo.get_all(skip=skip, limit=limit)

    def get_contract(self, contract_id: int) -> Contract:
        """
        Fetch a single contract.

        Args:
            contract_id: Contract primary key.

        Returns:
            Contract instance.

        Raises:
            ContractNotFoundError: Not found.
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise ContractNotFoundError(f"Contract {contract_id} not found.")
        return contract

    def create_contract(
        self,
        payload: ContractCreate,
    ) -> Contract:
        """
        Create a new contract.

        Args:
            payload: Contract creation data.

        Returns:
            Created Contract instance.
        """
        contract = Contract(
            client_id=payload.client_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            billing_cycle=payload.billing_cycle,
            auto_renew=payload.auto_renew,
            status=ContractStatus.ACTIVE,
        )
        return self.contract_repo.create(contract)

    def update_contract(
        self,
        contract_id: int,
        payload: ContractUpdate,
    ) -> Contract:
        """
        Apply partial update to a contract.

        Args:
            contract_id: Contract primary key.
            payload: Fields to update.

        Returns:
            Updated Contract instance.

        Raises:
            ContractNotFoundError: Not found.
        """
        contract = self.get_contract(contract_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(contract, field, value)
        self.db.flush()
        return contract

    def pause_contract(self, contract_id: int) -> Contract:
        """
        Pause an active contract.

        Args:
            contract_id: Contract primary key.

        Returns:
            Updated Contract with PAUSED status.

        Raises:
            ContractNotFoundError: Not found.
            ContractExpiredError: Already cancelled.
        """
        contract = self.get_contract(contract_id)
        if contract.status in (
            ContractStatus.CANCELLED,
            ContractStatus.EXPIRED,
        ):
            raise ContractExpiredError(
                "Cannot pause a cancelled/expired contract."
            )
        contract.status = ContractStatus.PAUSED
        self.db.flush()
        return contract

    def cancel_contract(self, contract_id: int) -> Contract:
        """
        Cancel a contract and void all pending
        invoices.

        All three steps are staged via flush() and
        committed atomically by the Unit of Work.

        Args:
            contract_id: Primary key of the contract.

        Returns:
            Updated Contract instance.

        Raises:
            ContractNotFoundError: Contract not found.
            ContractExpiredError: Already cancelled.
        """
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise ContractNotFoundError(f"Contract {contract_id} not found.")
        if contract.status == ContractStatus.CANCELLED:
            raise ContractExpiredError("Contract is already cancelled.")

        # Step 1: cancel the contract
        contract.status = ContractStatus.CANCELLED
        self.db.flush()

        # Step 2: void all non-paid linked invoices
        pending = self.invoice_repo.get_pending_by_contract(contract_id)
        for invoice in pending:
            invoice.status = InvoiceStatus.VOID
            self.db.flush()

        # Step 3: write audit log entry
        log = AuditLog(
            entity="contract",
            entity_id=contract_id,
            action="CANCELLED",
        )
        self.db.add(log)

        # get_db commits steps 1, 2, 3 as one unit
        return contract

    def get_contract_by_uid(self, internal_id: uuid.UUID) -> Contract:
        """Fetch contract by UUID7."""
        contract = self.contract_repo.get_by_internal_id(internal_id)
        if not contract:
            raise ContractNotFoundError(f"Contract {internal_id} not found.")
        return contract

    def update_contract_by_uid(
        self, internal_id: uuid.UUID, payload: ContractUpdate
    ) -> Contract:
        """Update contract by UUID7."""
        contract = self.get_contract_by_uid(internal_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(contract, field, value)
        self.db.flush()
        return contract

    def pause_contract_by_uid(self, internal_id: uuid.UUID) -> Contract:
        """Pause active contract by UUID7."""
        contract = self.get_contract_by_uid(internal_id)
        if contract.status in (
            ContractStatus.CANCELLED,
            ContractStatus.EXPIRED,
        ):
            raise ContractExpiredError(
                "Cannot pause a cancelled/expired contract."
            )
        contract.status = ContractStatus.PAUSED
        self.db.flush()
        return contract

    def cancel_contract_by_uid(self, internal_id: uuid.UUID) -> Contract:
        """Cancel contract and void pending invoices by UUID7."""
        contract = self.get_contract_by_uid(internal_id)
        if contract.status == ContractStatus.CANCELLED:
            raise ContractExpiredError("Contract is already cancelled.")

        contract.status = ContractStatus.CANCELLED
        self.db.flush()

        pending = self.invoice_repo.get_pending_by_contract(contract.id)
        for invoice in pending:
            invoice.status = InvoiceStatus.VOID
            self.db.flush()

        log = AuditLog(
            entity="contract",
            entity_id=contract.id,
            action="CANCELLED",
        )
        self.db.add(log)
        return contract
