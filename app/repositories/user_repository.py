# Standard library

# Third-party
from sqlalchemy.orm import Session

# Local
from app.models import User
from app.repositories import (
    BaseRepository,
)


class UserRepository(BaseRepository[User]):
    """
    Data access layer for User records.
    Extends BaseRepository with auth-specific queries.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        """
        Fetch a user by their email address.

        Args:
            email: Email address to search for.

        Returns:
            User if found, else None.
        """
        return self.db.query(User).filter(User.email == email).first()
