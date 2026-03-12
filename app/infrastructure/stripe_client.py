# Third-party
import stripe

# Local
from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClient:
    """
    Wraps the Stripe SDK for payment operations.
    API key is set globally from settings at import.
    """

    @staticmethod
    def construct_event(
        payload: bytes,
        sig_header: str,
        webhook_secret: str,
    ) -> stripe.Event:
        """
        Validate and construct a Stripe webhook event.

        Args:
            payload: Raw request body bytes.
            sig_header: Stripe-Signature header value.
            webhook_secret: Endpoint signing secret.

        Returns:
            Verified Stripe Event object.

        Raises:
            stripe.error.SignatureVerificationError:
                If the signature is invalid.
        """
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )

    @staticmethod
    def create_payment_intent(
        amount: int,
        currency: str,
        metadata: dict,
    ) -> stripe.PaymentIntent:
        """
        Create a Stripe PaymentIntent.

        Args:
            amount: Amount in smallest currency unit.
            currency: Three-letter ISO currency code.
            metadata: Key-value metadata dict.

        Returns:
            Created PaymentIntent object.
        """
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata=metadata,
        )
