# Standard library

# Third-party
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)

# Local
from app.api.deps import get_invoice_service
from app.config import settings
from app.services import InvoiceService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/webhook/stripe",
    status_code=status.HTTP_200_OK,
)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    service: InvoiceService = Depends(get_invoice_service),
) -> dict[str, str]:
    """
    Receive and process Stripe webhook events.
    Validates signature and handles idempotently.
    """
    import stripe

    from app.infrastructure.stripe_client import (
        StripeClient,
    )

    payload = await request.body()
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    if not webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe webhook secret not configured.",
        )

    try:
        event = StripeClient.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            webhook_secret=webhook_secret,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe signature.",
        )

    if event["type"] == "payment_intent.succeeded":
        service.handle_stripe_webhook(
            event_id=event["id"],
            payload=dict(event),
        )

    return {"status": "received"}
