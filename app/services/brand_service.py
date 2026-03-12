# Third-party
from sqlalchemy.orm import Session

# Local
from app.infrastructure.s3_client import S3Client
from app.models import BrandSettings
from app.repositories import (
    BrandRepository,
)
from app.schemas import BrandSettingsUpdate


class BrandService:
    """
    Manages workspace branding configuration.
    Handles logo upload to S3 and settings updates.

    Note: No direct commit() calls here —
    the Unit of Work in get_db owns all commits.
    """

    def __init__(
        self,
        db: Session,
        s3: S3Client,
    ) -> None:
        self.db = db
        self.brand_repo = BrandRepository(db)
        self.s3 = s3

    def get_brand(self) -> BrandSettings:
        """
        Return current brand settings, initialising
        NexBill defaults if not yet configured.
        """
        return self.brand_repo.get_or_create_defaults()

    def update_brand(
        self,
        payload: BrandSettingsUpdate,
    ) -> BrandSettings:
        """
        Apply partial brand settings update.

        Args:
            payload: Fields to update (PATCH style).

        Returns:
            Updated BrandSettings instance.
        """
        brand = self.brand_repo.get_or_create_defaults()
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(brand, field, value)

        # flush() only — get_db commits
        self.db.flush()
        return brand

    def upload_logo(
        self,
        file_bytes: bytes,
        content_type: str,
    ) -> BrandSettings:
        """
        Upload a new logo to S3 and store the URL.

        Args:
            file_bytes: Raw image file content.
            content_type: MIME type (image/png etc.).

        Returns:
            Updated BrandSettings with new logo_url.
        """
        logo_url = self.s3.upload(
            key="brand/logo",
            data=file_bytes,
            content_type=content_type,
        )
        brand = self.brand_repo.get_or_create_defaults()
        brand.logo_url = logo_url

        # flush() only — get_db commits
        self.db.flush()
        return brand

    def reset_to_defaults(self) -> BrandSettings:
        """
        Reset all branding fields back to the
        NexBill defaults. Logo URL reference cleared.

        Returns:
            BrandSettings reset to defaults.
        """
        brand = self.brand_repo.get_or_create_defaults()
        brand.brand_name = "NexBill"
        brand.logo_url = None
        brand.primary_color = "#1A56DB"
        brand.accent_color = "#7E3AF2"
        brand.invoice_prefix = "INV"
        brand.footer_text = None
        brand.support_email = None
        brand.website = None

        # flush() only — get_db commits
        self.db.flush()
        return brand
