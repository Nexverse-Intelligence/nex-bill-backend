# Standard library

# Third-party
from sqlalchemy.orm import Session

# Local
from app.infrastructure.email_client import (
    EmailClient,
)
from app.models import Invoice
from app.services import BrandService


class EmailService:
    """
    Sends transactional emails using the active brand
    name and reply-to address.
    """

    def __init__(
        self,
        db: Session,
        client: EmailClient,
        brand_service: BrandService,
    ) -> None:
        self.db = db
        self.client = client
        self.brand_service = brand_service

    def send_invoice(
        self,
        invoice: Invoice,
        recipient: str,
    ) -> None:
        """
        Email an invoice PDF to the recipient using
        the active brand name and support email.

        Args:
            invoice: Invoice to send.
            recipient: Recipient email address.
        """
        brand = self.brand_service.get_brand()
        self.client.send(
            from_name=brand.brand_name,
            reply_to=brand.support_email,
            to=recipient,
            subject=(f"Invoice from {brand.brand_name}"),
            template="invoice_email",
            context={
                "invoice": invoice,
                "brand": brand,
            },
        )

    def send_payment_receipt(
        self,
        invoice: Invoice,
        recipient: str,
    ) -> None:
        """
        Send a payment receipt to the client.

        Args:
            invoice: Fully or partially paid invoice.
            recipient: Recipient email address.
        """
        brand = self.brand_service.get_brand()
        self.client.send(
            from_name=brand.brand_name,
            reply_to=brand.support_email,
            to=recipient,
            subject=(f"Payment received — {brand.brand_name}"),
            template="payment_receipt",
            context={
                "invoice": invoice,
                "amount_paid": invoice.amount_paid,
                "brand": brand,
            },
        )
