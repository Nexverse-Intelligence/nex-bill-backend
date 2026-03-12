# Standard library

# Third-party
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment
    variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────
    SECRET_KEY: str = Field(
        default="change-me-in-production",
    )
    ALGORITHM: str = Field(
        default="HS256",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
    )

    # ── Database ─────────────────────────────────
    DATABASE_URL: str = Field(
        default=("postgresql://nexbill:nexbill@localhost:5432/nexbill"),
    )

    # ── Redis ────────────────────────────────────
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
    )

    # ── Celery ───────────────────────────────────
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
    )

    # ── AWS / S3 ─────────────────────────────────
    AWS_ACCESS_KEY_ID: str | None = Field(
        default=None,
    )
    AWS_SECRET_ACCESS_KEY: str | None = Field(
        default=None,
    )
    AWS_REGION: str = Field(
        default="us-east-1",
    )
    S3_BUCKET: str = Field(
        default="nexbill-assets",
    )
    S3_ENDPOINT_URL: str | None = Field(
        default=None,
    )

    # ── Email ────────────────────────────────────
    SENDGRID_API_KEY: str | None = Field(
        default=None,
    )
    EMAIL_FROM: str = Field(
        default="noreply@nexbill.app",
    )
    EMAIL_FROM_NAME: str = Field(
        default="NexBill",
    )

    # ── Stripe ───────────────────────────────────
    STRIPE_SECRET_KEY: str | None = Field(
        default=None,
    )
    STRIPE_WEBHOOK_SECRET: str | None = Field(
        default=None,
    )

    # ── CORS ─────────────────────────────────────
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
    )

    @property
    def allowed_origin_list(self) -> list[str]:
        """Return CORS origins as a list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ── Environment ──────────────────────────────
    ENVIRONMENT: str = Field(
        default="development",
    )
    DEBUG: bool = Field(
        default=False,
    )


settings = Settings()
