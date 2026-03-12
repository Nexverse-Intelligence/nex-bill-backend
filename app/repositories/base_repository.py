# Standard library
import uuid
from datetime import datetime
from typing import Generic, TypeVar

# Third-party
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository providing standard CRUD
    operations for all domain entities.

    Repositories call flush() only — never commit().
    Transaction boundaries are owned by the service
    layer exclusively via the Unit of Work.
    """

    def __init__(
        self,
        model: type[ModelType],
        db: Session,
    ) -> None:
        self.model = model
        self.db = db

    def get_by_id(self, record_id: int) -> ModelType | None:
        """Fetch a single record by integer primary key."""
        return (
            self.db.query(self.model)
            .filter(self.model.id == record_id)  # type: ignore[attr-defined]
            .first()
        )

    def get_by_internal_id(self, internal_id: uuid.UUID) -> ModelType | None:
        """
        Fetch a single record by its public UUID7
        ``internal_id``.

        This is the lookup method used by API endpoints
        that receive UUID path parameters from the
        frontend / external consumers.

        Args:
            internal_id: UUID7 value from the request.

        Returns:
            Model instance or None.
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.internal_id  # type: ignore[attr-defined]
                == internal_id
            )
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Fetch a paginated list of records."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        """Persist a new record to the session."""
        self.db.add(obj)
        self.db.flush()
        return obj

    def soft_delete(self, obj: ModelType) -> None:
        """
        Mark record as deleted without removing it.
        Requires a deleted_at column on the model.
        """
        obj.deleted_at = datetime.utcnow()  # type: ignore[attr-defined]
        self.db.flush()
