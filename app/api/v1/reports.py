# Standard library
from typing import Any

# Third-party
from fastapi import APIRouter, Depends, Query

# Local
from app.api.deps import CurrentUser, get_report_service
from app.services import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/revenue")
def revenue_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = None,
) -> dict[str, Any]:
    """Revenue summary for a given year/month."""
    return service.revenue_summary(year, month)


@router.get("/aging")
def aging_receivables(
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = None,
) -> list[dict[str, Any]]:
    """Aging receivables grouped by days overdue."""
    return service.aging_receivables()


@router.get("/tax-summary")
def tax_summary(
    year: int = Query(..., ge=2000, le=2100),
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = None,
) -> dict[str, Any]:
    """Tax summary for a given year."""
    return service.tax_summary(year)
