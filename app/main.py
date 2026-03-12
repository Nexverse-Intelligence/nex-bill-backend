# Standard library

# Third-party
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Local
from app.api.v1 import (
    auth,
    brand,
    clients,
    contracts,
    invoices,
    payments,
    reports,
)
from app.config import settings
from app.exceptions import (
    ClientNotFoundError,
    ContractExpiredError,
    ContractNotFoundError,
    ForbiddenError,
    InvalidPaymentError,
    InvoiceNotFoundError,
    UnauthorizedError,
)

app = FastAPI(
    title="NexBill API",
    description=("Invoice Management System — REST API"),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handlers ────────────────────────


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(
    request: Request,
    exc: UnauthorizedError,
) -> JSONResponse:
    """Convert UnauthorizedError to HTTP 401."""
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(
    request: Request,
    exc: ForbiddenError,
) -> JSONResponse:
    """Convert ForbiddenError to HTTP 403."""
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvoiceNotFoundError)
async def invoice_not_found_handler(
    request: Request,
    exc: InvoiceNotFoundError,
) -> JSONResponse:
    """Convert InvoiceNotFoundError to HTTP 404."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(ClientNotFoundError)
async def client_not_found_handler(
    request: Request,
    exc: ClientNotFoundError,
) -> JSONResponse:
    """Convert ClientNotFoundError to HTTP 404."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(ContractNotFoundError)
async def contract_not_found_handler(
    request: Request,
    exc: ContractNotFoundError,
) -> JSONResponse:
    """Convert ContractNotFoundError to HTTP 404."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidPaymentError)
async def invalid_payment_handler(
    request: Request,
    exc: InvalidPaymentError,
) -> JSONResponse:
    """Convert InvalidPaymentError to HTTP 400."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(ContractExpiredError)
async def contract_expired_handler(
    request: Request,
    exc: ContractExpiredError,
) -> JSONResponse:
    """Convert ContractExpiredError to HTTP 409."""
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


# ── Routers ──────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(clients.router, prefix=API_PREFIX)
app.include_router(invoices.router, prefix=API_PREFIX)
app.include_router(contracts.router, prefix=API_PREFIX)
app.include_router(payments.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(brand.router, prefix=API_PREFIX)


# ── Health check ─────────────────────────────────────


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """Liveness probe endpoint."""
    return {"status": "ok"}
