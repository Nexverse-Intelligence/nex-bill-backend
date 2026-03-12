# Standard library
from typing import Any

# Local
from app.infrastructure.celery_app import celery_app
from app.infrastructure.database import get_db_context
from app.services import InvoiceService


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_recurring_invoices(self: Any) -> None:
    """
    Celery task: generate all due recurring invoices.

    Uses get_db_context() for the same Unit of Work
    guarantees as the FastAPI get_db dependency.
    Retries up to 3 times with a 60s delay.
    """
    try:
        with get_db_context() as db:
            service = InvoiceService(db)
            service.generate_due_recurring_invoices()
            # context manager commits on clean exit
    except Exception as exc:
        raise self.retry(exc=exc)
