# Standard library
from typing import Any

# Local
from app.infrastructure.celery_app import celery_app
from app.infrastructure.database import get_db_context
from app.infrastructure.email_client import EmailClient
from app.infrastructure.s3_client import S3Client
from app.services import BrandService, EmailService, InvoiceService


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_invoice_email(
    self: Any,
    invoice_id: int,
    recipient: str,
) -> None:
    """
    Celery task: send an invoice email.

    Args:
        invoice_id: Invoice primary key to send.
        recipient: Target email address.
    """
    try:
        with get_db_context() as db:
            invoice_service = InvoiceService(db)
            invoice = invoice_service.get_invoice(invoice_id)
            brand_service = BrandService(db, S3Client())
            email_service = EmailService(
                db=db,
                client=EmailClient(),
                brand_service=brand_service,
            )
            email_service.send_invoice(
                invoice=invoice,
                recipient=recipient,
            )
    except Exception as exc:
        raise self.retry(exc=exc)
