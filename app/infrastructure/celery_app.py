# Third-party
from celery import Celery

# Local
from app.config import settings

celery_app = Celery(
    "nexbill",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "generate-recurring-invoices-daily": {
            "task": ("app.tasks.invoice_tasks.generate_recurring_invoices"),
            "schedule": 86400,  # every 24 hours
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
