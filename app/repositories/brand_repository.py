# Standard library

# Third-party
from sqlalchemy.orm import Session

# Local
from app.models import BrandSettings
from app.repositories import (
    BaseRepository,
)


class BrandRepository(BaseRepository[BrandSettings]):
    """
    Data access layer for workspace branding config.
    Always operates on a single settings row.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(BrandSettings, db)

    def get_settings(
        self,
    ) -> BrandSettings | None:
        """
        Fetch the current workspace brand config.
        Returns None if not yet initialised.
        """
        return self.db.query(BrandSettings).first()

    def get_or_create_defaults(
        self,
    ) -> BrandSettings:
        """
        Return existing settings or create a default
        NexBill config if none exists yet.
        """
        settings = self.get_settings()
        if settings:
            return settings
        defaults = BrandSettings()
        self.db.add(defaults)
        self.db.flush()
        return defaults
