# Standard library

# Third-party
from sqlalchemy.orm import Session

# Local
from app.models import Client
from app.repositories import (
    BaseRepository,
)


class ClientRepository(BaseRepository[Client]):
    """
    Data access layer for Client records.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Client, db)

    def get_active(self, skip: int = 0, limit: int = 100) -> list[Client]:
        """
        Fetch non-deleted clients with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of active Client records.
        """
        return (
            self.db.query(Client)
            .filter(Client.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_name(self, name: str) -> list[Client]:
        """
        Search clients by name substring.

        Args:
            name: Partial name to search for.

        Returns:
            Matching active Client records.
        """
        return (
            self.db.query(Client)
            .filter(
                Client.deleted_at.is_(None),
                Client.name.ilike(f"%{name}%"),
            )
            .all()
        )
