# Standard library
from typing import Annotated

# Third-party
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# Local
from app.exceptions import UnauthorizedError
from app.infrastructure.database import get_db
from app.infrastructure.email_client import EmailClient
from app.infrastructure.s3_client import S3Client
from app.models import User
from app.repositories import (
    UserRepository,
)
from app.services import (
    AuthService,
    BrandService,
    ClientService,
    ContractService,
    InvoiceService,
    PaymentService,
    PdfService,
    ReportService,
)

security = HTTPBearer()

DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
) -> User:
    """
    Decode JWT and return the current User.

    Raises:
        HTTPException 401: Token invalid or expired.
        HTTPException 401: User not found.
    """
    try:
        payload = AuthService.decode_token(credentials.credentials)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload["sub"])
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(
    current_user: CurrentUser,
) -> User:
    """
    Enforce admin role on a route.

    Raises:
        HTTPException 403: User is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


# ── Service factories ────────────────────────────────


def get_auth_service(db: DbDep) -> AuthService:
    """Provide an AuthService instance."""
    return AuthService(db)


def get_client_service(db: DbDep) -> ClientService:
    """Provide a ClientService instance."""
    return ClientService(db)


def get_invoice_service(db: DbDep) -> InvoiceService:
    """Provide an InvoiceService instance."""
    return InvoiceService(db)


def get_contract_service(
    db: DbDep,
) -> ContractService:
    """Provide a ContractService instance."""
    return ContractService(db)


def get_payment_service(db: DbDep) -> PaymentService:
    """Provide a PaymentService instance."""
    return PaymentService(db)


def get_report_service(db: DbDep) -> ReportService:
    """Provide a ReportService instance."""
    return ReportService(db)


def get_s3() -> S3Client:
    """Provide an S3Client instance."""
    return S3Client()


def get_email_client() -> EmailClient:
    """Provide an EmailClient instance."""
    return EmailClient()


def get_brand_service(
    db: DbDep,
    s3: Annotated[S3Client, Depends(get_s3)],
) -> BrandService:
    """Provide a BrandService instance."""
    return BrandService(db, s3)


def get_pdf_service(
    db: DbDep,
    s3: Annotated[S3Client, Depends(get_s3)],
) -> PdfService:
    """Provide a PdfService instance."""
    brand = BrandService(db, s3).get_brand()
    return PdfService(brand)
