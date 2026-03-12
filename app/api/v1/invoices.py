# Standard library
import uuid

# Third-party
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

# Local
from app.api.deps import (
    CurrentUser,
    get_invoice_service,
    get_pdf_service,
)
from app.enums import InvoiceStatus
from app.exceptions import (
    ClientNotFoundError,
    InvalidPaymentError,
    InvoiceNotFoundError,
)
from app.schemas import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
    PaymentCreate,
)
from app.services import InvoiceService, PdfService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("/", response_model=InvoiceListResponse)
def list_invoices(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    status_filter: InvoiceStatus | None = Query(default=None, alias="status"),
    service: InvoiceService = Depends(get_invoice_service),
    current_user: CurrentUser = None,
) -> InvoiceListResponse:
    """List invoices with optional status filter."""
    invoices, total = service.list_invoices(
        skip=skip, limit=limit, status=status_filter
    )
    return InvoiceListResponse(
        items=invoices, total=total, skip=skip, limit=limit
    )


@router.post(
    "/",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    payload: InvoiceCreate,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: CurrentUser = None,
) -> InvoiceResponse:
    """Create a new invoice with line items."""
    try:
        return service.create_invoice(payload, created_by=current_user.id)
    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/{internal_id}",
    response_model=InvoiceResponse,
)
def get_invoice(
    internal_id: uuid.UUID,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: CurrentUser = None,
) -> InvoiceResponse:
    """Retrieve a single invoice by its UUID7."""
    try:
        return service.get_invoice_by_uid(internal_id)
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.put(
    "/{internal_id}",
    response_model=InvoiceResponse,
)
def update_invoice(
    internal_id: uuid.UUID,
    payload: InvoiceUpdate,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: CurrentUser = None,
) -> InvoiceResponse:
    """Update an invoice identified by its UUID7."""
    try:
        return service.update_invoice_by_uid(internal_id, payload)
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{internal_id}/send",
    response_model=InvoiceResponse,
)
def send_invoice(
    internal_id: uuid.UUID,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: CurrentUser = None,
) -> InvoiceResponse:
    """Transition invoice from DRAFT to SENT."""
    try:
        return service.send_invoice_by_uid(internal_id)
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except InvalidPaymentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{internal_id}/payments",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_payment(
    internal_id: uuid.UUID,
    payload: PaymentCreate,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: CurrentUser = None,
) -> InvoiceResponse:
    """Record a payment against an invoice by UUID7."""
    try:
        return service.record_payment_by_uid(
            internal_id=internal_id,
            amount=payload.amount,
            method=payload.method,
            provider_ref=payload.provider_ref,
        )
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except InvalidPaymentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{internal_id}/pdf")
def get_invoice_pdf(
    internal_id: uuid.UUID,
    invoice_service: InvoiceService = Depends(get_invoice_service),
    pdf_service: PdfService = Depends(get_pdf_service),
    current_user: CurrentUser = None,
) -> Response:
    """Download an invoice as PDF, identified by UUID7."""
    try:
        invoice = invoice_service.get_invoice_by_uid(internal_id)
        pdf_bytes = pdf_service.render_invoice(invoice)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=invoice-{internal_id}.pdf"
                )
            },
        )
    except InvoiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
