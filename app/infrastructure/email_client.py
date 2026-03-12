# Standard library
from typing import Any

# Third-party
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Content,
    Email,
    Mail,
    To,
)

# Local
from app.config import settings


class EmailClient:
    """
    Wraps the SendGrid SDK for transactional emails.
    """

    def __init__(self) -> None:
        self._client = SendGridAPIClient(
            api_key=settings.SENDGRID_API_KEY or ""
        )
        self._from_email = settings.EMAIL_FROM
        self._from_name = settings.EMAIL_FROM_NAME

    def send(
        self,
        to: str,
        subject: str,
        template: str,
        context: dict[str, Any],
        from_name: str | None = None,
        reply_to: str | None = None,
    ) -> None:
        """
        Send a transactional email.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            template: Template name identifier.
            context: Template rendering context.
            from_name: Override sender display name.
            reply_to: Reply-to email address.
        """
        sender_name = from_name or self._from_name
        html_content = self._render(template, context)

        message = Mail(
            from_email=Email(self._from_email, sender_name),
            to_emails=To(to),
            subject=subject,
            html_content=Content("text/html", html_content),
        )
        if reply_to:
            message.reply_to = Email(reply_to)

        self._client.send(message)

    @staticmethod
    def _render(
        template: str,
        context: dict[str, Any],
    ) -> str:
        """
        Render a named template with context.

        Args:
            template: Template name.
            context: Template variables dict.

        Returns:
            Rendered HTML string.
        """
        # Simple placeholder — replace with Jinja2
        # template loading in production use.
        parts = [
            f"<strong>{k}:</strong> {v}"
            for k, v in context.items()
            if not hasattr(v, "__dict__")
        ]
        return "<br>".join(parts)
