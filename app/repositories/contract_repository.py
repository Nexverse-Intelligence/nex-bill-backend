# Standard library
from datetime import date

# Third-party
from sqlalchemy.orm import Session

# Local
from app.enums import ContractStatus
from app.models import Contract
from app.repositories import (
    BaseRepository,
)


class ContractRepository(BaseRepository[Contract]):
    """
    Data access layer for Contract records.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Contract, db)

    def get_active_for_renewal(
        self,
    ) -> list[Contract]:
        """
        Fetch active contracts past their end_date
        with auto_renew enabled.

        Returns:
            Active, auto-renewing expired contracts.
        """
        today = date.today()
        return (
            self.db.query(Contract)
            .filter(
                Contract.status == ContractStatus.ACTIVE,
                Contract.auto_renew.is_(True),
                Contract.end_date <= today,
            )
            .all()
        )
