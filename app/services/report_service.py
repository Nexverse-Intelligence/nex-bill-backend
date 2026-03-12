# Standard library
from datetime import date
from decimal import Decimal
from typing import Any

# Third-party
from sqlalchemy import func
from sqlalchemy.orm import Session

# Local
from app.enums import InvoiceStatus
from app.models import Invoice


class ReportService:
    """
    Generates financial summary reports:
    revenue, aging receivables, and tax summaries.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def revenue_summary(
        self,
        year: int,
        month: int | None = None,
    ) -> dict[str, Any]:
        """
        Compute total revenue for a period.

        Args:
            year: Target year.
            month: Optional target month (1-12).

        Returns:
            Dict with total_billed and total_paid.
        """
        query = self.db.query(Invoice).filter(
            func.extract("year", Invoice.created_at) == year,
            Invoice.status.in_(
                [
                    InvoiceStatus.PAID,
                    InvoiceStatus.PARTIALLY_PAID,
                    InvoiceStatus.SENT,
                ]
            ),
        )
        if month:
            query = query.filter(
                func.extract("month", Invoice.created_at) == month
            )

        invoices = query.all()
        total_billed = sum(i.total_amount for i in invoices)
        total_paid = sum(i.amount_paid for i in invoices)
        return {
            "year": year,
            "month": month,
            "total_billed": total_billed,
            "total_paid": total_paid,
            "outstanding": total_billed - total_paid,
        }

    def aging_receivables(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all unpaid invoices grouped by how
        far past due they are (0-30, 31-60, 60+).

        Returns:
            List of aging buckets with totals.
        """
        today = date.today()
        unpaid = (
            self.db.query(Invoice)
            .filter(
                Invoice.status.in_(
                    [
                        InvoiceStatus.SENT,
                        InvoiceStatus.PARTIALLY_PAID,
                        InvoiceStatus.OVERDUE,
                    ]
                )
            )
            .all()
        )

        buckets: dict[str, Decimal] = {
            "current": Decimal("0"),
            "1_30_days": Decimal("0"),
            "31_60_days": Decimal("0"),
            "over_60_days": Decimal("0"),
        }

        for inv in unpaid:
            outstanding = inv.total_amount - inv.amount_paid
            days_overdue = (today - inv.due_date).days
            if days_overdue <= 0:
                buckets["current"] += outstanding
            elif days_overdue <= 30:
                buckets["1_30_days"] += outstanding
            elif days_overdue <= 60:
                buckets["31_60_days"] += outstanding
            else:
                buckets["over_60_days"] += outstanding

        return [{"bucket": k, "total": v} for k, v in buckets.items()]

    def tax_summary(
        self,
        year: int,
    ) -> dict[str, Any]:
        """
        Compute total tax collected for a year.

        Args:
            year: Target year.

        Returns:
            Dict with total_tax_collected.
        """
        paid_invoices = (
            self.db.query(Invoice)
            .filter(
                func.extract("year", Invoice.created_at) == year,
                Invoice.status == InvoiceStatus.PAID,
            )
            .all()
        )

        total_tax = Decimal("0")
        for inv in paid_invoices:
            for item in inv.items:
                line = (
                    item.quantity * item.unit_price * (1 - item.discount / 100)
                )
                total_tax += line * item.tax_rate / 100

        return {
            "year": year,
            "total_tax_collected": total_tax,
        }
