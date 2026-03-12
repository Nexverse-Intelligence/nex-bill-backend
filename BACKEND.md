# Invoice Management System — Backend

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Framework    | Python 3.11+ + FastAPI              |
| Database     | PostgreSQL 15+                      |
| ORM          | SQLAlchemy 2.x                      |
| Migrations   | Alembic                             |
| Cache        | Redis 7+                            |
| Task Queue   | Celery 5 + Redis broker             |
| Auth         | python-jose, passlib (bcrypt)       |
| Payments     | Stripe SDK, PayPal SDK              |
| Email        | SendGrid / AWS SES                  |
| Accounting   | QuickBooks / Xero REST APIs         |
| File Storage | MinIO / AWS S3                      |
| Testing      | pytest, pytest-asyncio, httpx       |
| Linting      | ruff, black, isort, mypy            |

---

## Architectural Style

The backend follows a **Layered Architecture** with the
**Repository Pattern** to cleanly separate concerns.

```
┌──────────────────────────────────────────────┐
│                  API Layer                   │
│      (FastAPI Routers / Route Handlers)      │
├──────────────────────────────────────────────┤
│               Service Layer                  │
│        (Business Logic / Use Cases)          │
├──────────────────────────────────────────────┤
│             Repository Layer                 │
│      (Data Access Abstraction / ORM)         │
├──────────────────────────────────────────────┤
│               Domain Layer                   │
│      (Models, Schemas, Enums, Types)         │
├──────────────────────────────────────────────┤
│           Infrastructure Layer               │
│  (DB, Redis, S3, Email, Stripe, Celery)      │
└──────────────────────────────────────────────┘
```

> **Rule:** Dependencies only flow **downward**.
> Services depend on Repositories — never the reverse.
> The API layer must not contain business logic or
> direct DB queries.

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── clients.py
│   │   │   ├── contracts.py
│   │   │   ├── invoices.py
│   │   │   ├── payments.py
│   │   │   └── reports.py
│   │   └── deps.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── brand_service.py
│   │   ├── client_service.py
│   │   ├── contract_service.py
│   │   ├── invoice_service.py
│   │   ├── payment_service.py
│   │   ├── pdf_service.py
│   │   ├── email_service.py
│   │   └── report_service.py
│   ├── repositories/
│   │   ├── base_repository.py
│   │   ├── brand_repository.py
│   │   ├── user_repository.py
│   │   ├── client_repository.py
│   │   ├── contract_repository.py
│   │   ├── invoice_repository.py
│   │   └── payment_repository.py
│   ├── models/
│   │   ├── brand_settings.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── invoice.py
│   │   └── payment.py
│   ├── schemas/
│   │   ├── auth_schema.py
│   │   ├── brand_schema.py
│   │   ├── client_schema.py
│   │   ├── contract_schema.py
│   │   ├── invoice_schema.py
│   │   └── payment_schema.py
│   ├── enums/
│   │   ├── invoice_status.py
│   │   └── contract_status.py
│   ├── infrastructure/
│   │   ├── database.py
│   │   ├── redis_client.py
│   │   ├── s3_client.py
│   │   ├── email_client.py
│   │   ├── stripe_client.py
│   │   └── celery_app.py
│   ├── tasks/
│   │   ├── invoice_tasks.py
│   │   └── email_tasks.py
│   ├── exceptions.py
│   ├── config.py
│   └── main.py
├── alembic/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml
├── .env.example
└── Dockerfile
```

---

## Coding Standards

### Line Length
- **Code:** maximum **79 characters** per line
- **Docstrings & comments:** maximum **72 characters**
  per line

### Naming Conventions

| Construct        | Convention         | Example                 |
|------------------|--------------------|-------------------------|
| Variable         | `snake_case`       | `invoice_total`         |
| Function/Method  | `snake_case`       | `create_invoice()`      |
| Class            | `PascalCase`       | `InvoiceService`        |
| Constant         | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`       |
| Module/file      | `snake_case`       | `invoice_service.py`    |
| Pydantic schema  | `PascalCase`       | `InvoiceCreateSchema`   |
| SQLAlchemy model | `PascalCase`       | `Invoice`               |
| Enum             | `PascalCase`       | `InvoiceStatus`         |
| Enum value       | `UPPER_SNAKE_CASE` | `InvoiceStatus.PAID`    |

### Imports
Order in three groups, separated by blank lines:
1. Standard library
2. Third-party packages
3. Local application modules

```python
# Standard library
from decimal import Decimal
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local
from app.services.invoice_service import InvoiceService
from app.api.deps import get_db, get_current_user
```

### Type Annotations
All functions and methods **must** include full type hints.

```python
from typing import Optional
from decimal import Decimal


def get_outstanding_balance(
    invoice_id: int,
    db: Session,
) -> Optional[Decimal]:
    """
    Retrieve the unpaid balance for a given invoice.

    Returns None if the invoice does not exist.
    """
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        return None
    return invoice.total_amount - invoice.amount_paid
```

### Docstring Style — Google Format

```python
def mark_as_paid(
    self,
    invoice_id: int,
    payment_amount: Decimal,
) -> Invoice:
    """
    Mark an invoice as fully or partially paid.

    Updates status based on whether payment_amount
    covers the full outstanding balance.

    Args:
        invoice_id: Primary key of the invoice.
        payment_amount: Amount being paid now.

    Returns:
        Updated Invoice domain model instance.

    Raises:
        InvoiceNotFoundError: Invoice not found.
        InvalidPaymentError: Amount exceeds total.
    """
    ...
```

### Linting & Formatting Config (`pyproject.toml`)

```toml
[tool.black]
line-length = 79
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 79

[tool.ruff]
line-length = 79
select = ["E", "F", "W", "I", "N", "UP"]

[tool.mypy]
strict = true
python_version = "3.11"
```

---

## Repository Pattern

### Base Repository

```python
# app/repositories/base_repository.py

from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository providing standard CRUD
    operations for all domain entities.

    Repositories call flush() only — never commit().
    Transaction boundaries are owned by the service
    layer exclusively.
    """

    def __init__(
        self,
        model: type[ModelType],
        db: Session,
    ) -> None:
        self.model = model
        self.db = db

    def get_by_id(
        self, record_id: int
    ) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        return (
            self.db.query(self.model)
            .filter(self.model.id == record_id)
            .first()
        )

    def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Fetch a paginated list of records."""
        return (
            self.db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, obj: ModelType) -> ModelType:
        """Persist a new record to the session."""
        self.db.add(obj)
        self.db.flush()
        return obj

    def soft_delete(self, obj: ModelType) -> None:
        """
        Mark record as deleted without removing it.
        Requires a deleted_at column on the model.
        """
        obj.deleted_at = datetime.utcnow()
        self.db.flush()
```

### Example — Invoice Repository

```python
# app/repositories/invoice_repository.py

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.enums.invoice_status import InvoiceStatus
from app.repositories.base_repository import (
    BaseRepository,
)


class InvoiceRepository(BaseRepository[Invoice]):
    """
    Data access layer for Invoice records.
    Extends BaseRepository with invoice-specific
    query methods.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Invoice, db)

    def get_by_client(
        self, client_id: int
    ) -> List[Invoice]:
        """Fetch all invoices for a given client."""
        return (
            self.db.query(Invoice)
            .filter(Invoice.client_id == client_id)
            .order_by(Invoice.created_at.desc())
            .all()
        )

    def get_overdue(self) -> List[Invoice]:
        """Fetch all invoices past their due date."""
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.status == InvoiceStatus.SENT,
                Invoice.due_date < date.today(),
            )
            .all()
        )
```

---

## Atomicity & Transaction Handling

### Why Atomicity Matters

Invoice management involves multi-step financial
operations where partial success is unacceptable:

- Creating an invoice + its line items
- Recording a payment + updating invoice status
- Syncing to QuickBooks + updating sync flag
- Generating recurring invoice + updating contract
- Issuing a credit note + reversing payment records
- Cancelling a contract + voiding pending invoices

All such operations must **succeed entirely or not at
all**. Any failure must leave the database in its
original consistent state.

---

### Unit of Work via `get_db`

Rather than each service manually calling `commit()`
and `rollback()`, the session dependency itself acts
as the **Unit of Work**. It commits automatically
when the request succeeds and rolls back on any
unhandled exception — with zero boilerplate in
service methods.

**How it works:**

```
Request enters  →  get_db opens session
                       │
                  service flushes changes
                  (SQL staged, not written)
                       │
              ┌────────┴────────┐
        No exception         Exception raised
              │                    │
         db.commit()          db.rollback()
         ✅ persisted          ❌ all undone
              │                    │
         db.close()           db.close()
              └────────┬────────┘
                  Response sent
```

### flush() vs commit() vs rollback()

| Operation    | What it does                             |
|--------------|------------------------------------------|
| `flush()`    | Sends SQL to DB within the transaction;  |
|              | assigns PKs; still fully reversible      |
| `commit()`   | Permanently writes all flushed changes   |
| `rollback()` | Undoes everything flushed but uncommitted|

Repositories call `flush()` so auto-generated PKs
(e.g. `invoice.id`) are available for downstream
steps — all within the same open transaction.

---

### Transaction Ownership Rules

| Layer      | Responsibility                              |
|------------|---------------------------------------------|
| `get_db`   | Opens session; commits or rolls back        |
| Repository | `flush()` only — never `commit()`           |
| Service    | Business logic + `flush()`; no commit calls |
| API        | No DB ops — only raises exceptions          |
| Celery     | Uses `get_db_context()` — same UoW contract |

> No layer below `get_db` ever calls `commit()` or
> `rollback()` directly. Violating this rule would
> silently split a multi-step operation across two
> separate transactions.

---

### Implementation

#### `get_db` — Unit of Work Dependency

```python
# app/infrastructure/database.py

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    FastAPI dependency implementing Unit of Work.

    Yields a session for the duration of the request.
    Commits on clean exit; rolls back on any exception.
    Guarantees the session is closed either way.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()       # success — persist all
    except Exception:
        db.rollback()     # failure — undo all
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager version of get_db for use in
    Celery tasks and scripts outside of FastAPI.

    Usage:
        with get_db_context() as db:
            InvoiceService(db).create_invoice(...)
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

---

### Transaction Flow Diagram (with UoW)

```
HTTP Request
  │
  ▼
get_db() opens session
  │
  ▼
API route calls service method
  │
  ├── invoice_repo.create(invoice)   → flush()
  │       └── invoice.id assigned (PK available)
  ├── item_repo.create(item_1)       → flush()
  ├── item_repo.create(item_2)       → flush()
  ├── audit_repo.create(log)         → flush()
  │
  ▼
service returns result to API
  │
  ▼
get_db() resumes after yield
  │
  ├── No exception → db.commit()   ✅ all persisted
  └── Exception    → db.rollback() ❌ all undone
                     re-raise → HTTP 4xx/5xx
```

---

### Service Layer — No Commit Needed

Services now only contain business logic and `flush()`
calls. All transaction control has moved to `get_db`.

```python
# app/services/invoice_service.py

class InvoiceService:
    """
    Manages invoice lifecycle: creation, status
    transitions, PDF generation, and payment
    reconciliation. Transaction is handled by the
    Unit of Work (get_db dependency).
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.item_repo = InvoiceItemRepository(db)

    def create_invoice(
        self,
        payload: InvoiceCreate,
    ) -> Invoice:
        """
        Create an invoice with all its line items.

        No commit/rollback here — the Unit of Work
        in get_db handles transaction boundaries.

        Args:
            payload: Validated invoice creation data.

        Returns:
            Flushed Invoice instance with PK assigned.

        Raises:
            ClientNotFoundError: Client not found.
        """
        invoice = Invoice(
            client_id=payload.client_id,
            due_date=payload.due_date,
            currency=payload.currency,
            status=InvoiceStatus.DRAFT,
        )
        # flush assigns invoice.id for use below
        self.invoice_repo.create(invoice)

        for item_data in payload.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data.model_dump(),
            )
            self.item_repo.create(item)

        # No commit — get_db commits after return
        return invoice

    def record_payment(
        self,
        invoice_id: int,
        amount: Decimal,
    ) -> Invoice:
        """
        Record a payment and update invoice status.

        Args:
            invoice_id: Target invoice primary key.
            amount: Payment amount being recorded.

        Returns:
            Updated Invoice instance.

        Raises:
            InvoiceNotFoundError: Invoice not found.
            InvalidPaymentError: Amount exceeds total.
        """
        invoice = self.invoice_repo.get_by_id(
            invoice_id
        )
        if not invoice:
            raise InvoiceNotFoundError(
                f"Invoice {invoice_id} not found."
            )

        new_paid = invoice.amount_paid + amount
        if new_paid > invoice.total_amount:
            raise InvalidPaymentError(
                "Payment exceeds invoice total."
            )

        # Step 1: create payment record
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            paid_at=datetime.utcnow(),
        )
        self.db.add(payment)
        self.db.flush()

        # Step 2: update invoice balance and status
        invoice.amount_paid = new_paid
        if new_paid >= invoice.total_amount:
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = (
                InvoiceStatus.PARTIALLY_PAID
            )
        self.db.flush()

        # get_db commits both steps together
        return invoice
```

---

### Nested Operations — Contract Cancellation

Multi-entity operations work cleanly. All `flush()`
calls stage changes; `get_db` commits them together.

```python
def cancel_contract(
    self,
    contract_id: int,
) -> Contract:
    """
    Cancel a contract and void all pending invoices.

    All three steps are staged via flush() and
    committed atomically by the Unit of Work.

    Args:
        contract_id: Primary key of the contract.

    Returns:
        Updated Contract instance.

    Raises:
        ContractNotFoundError: Contract not found.
        ContractExpiredError: Already cancelled.
    """
    contract = self.contract_repo.get_by_id(
        contract_id
    )
    if not contract:
        raise ContractNotFoundError(
            f"Contract {contract_id} not found."
        )
    if contract.status == ContractStatus.CANCELLED:
        raise ContractExpiredError(
            "Contract is already cancelled."
        )

    # Step 1: cancel the contract
    contract.status = ContractStatus.CANCELLED
    self.db.flush()

    # Step 2: void all non-paid linked invoices
    pending = (
        self.invoice_repo
        .get_pending_by_contract(contract_id)
    )
    for invoice in pending:
        invoice.status = InvoiceStatus.VOID
        self.db.flush()

    # Step 3: write audit log entry
    self.audit_repo.create(AuditLog(
        entity="contract",
        entity_id=contract_id,
        action="CANCELLED",
    ))

    # get_db commits steps 1, 2, 3 as one unit
    return contract
```

---

### Savepoint Pattern — Partial Batch Operations

For batch jobs where each item must be independently
isolated, use savepoints within the outer UoW session.

```python
def process_invoice_batch(
    self,
    invoice_ids: list[int],
) -> dict:
    """
    Send a batch of invoices. Each uses a savepoint
    so one failure does not affect the others.

    The outer UoW (get_db) commits all successful
    savepoints together at request end.

    Args:
        invoice_ids: List of invoice PKs to send.

    Returns:
        Dict with 'success' and 'failed' ID lists.
    """
    results: dict = {"success": [], "failed": []}

    for invoice_id in invoice_ids:
        # Savepoint per invoice — nested transaction
        savepoint = self.db.begin_nested()
        try:
            invoice = self.invoice_repo.get_by_id(
                invoice_id
            )
            invoice.status = InvoiceStatus.SENT
            self.db.flush()
            savepoint.commit()
            results["success"].append(invoice_id)

        except Exception:
            # Roll back this invoice only
            savepoint.rollback()
            results["failed"].append(invoice_id)

    # Outer UoW (get_db) commits all saved points
    return results
```

---

### Idempotency for Payment Webhooks

Stripe and PayPal can redeliver webhook events.
Use a `webhook_events` table as an idempotency guard.
The UoW ensures the guard record and payment are
written atomically — no partial states possible.

```python
def handle_stripe_webhook(
    self,
    event_id: str,
    payload: dict,
) -> None:
    """
    Process a Stripe webhook event idempotently.

    Skips if event_id already recorded. Otherwise,
    writes the guard record and applies the payment
    in one atomic unit via the UoW.

    Args:
        event_id: Unique Stripe event identifier.
        payload: Full webhook event payload dict.
    """
    existing = (
        self.db.query(WebhookEvent)
        .filter(WebhookEvent.event_id == event_id)
        .first()
    )
    if existing:
        # Already processed — safe to skip
        return

    # Write idempotency guard record
    event_record = WebhookEvent(
        event_id=event_id,
        processed_at=datetime.utcnow(),
    )
    self.db.add(event_record)
    self.db.flush()

    # Apply payment — both flushed, UoW commits
    self._apply_payment_from_webhook(payload)
```

---

### Celery Task Atomicity

Celery tasks run outside FastAPI's request lifecycle
so they cannot use `get_db` as a dependency. They use
`get_db_context()` — the same Unit of Work contract.

```python
# app/tasks/invoice_tasks.py

from app.infrastructure.database import get_db_context
from app.services.invoice_service import InvoiceService


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_recurring_invoices(self) -> None:
    """
    Celery task: generate all due recurring invoices.

    Uses get_db_context() for the same Unit of Work
    guarantees as the FastAPI get_db dependency.
    Retries up to 3 times with a 60s delay.
    """
    try:
        with get_db_context() as db:
            service = InvoiceService(db)
            service.generate_due_recurring_invoices()
            # context manager commits on clean exit
    except Exception as exc:
        raise self.retry(exc=exc)
```

---

### What Changed vs Manual Commit Pattern

| Concern            | Manual (old)           | Unit of Work (new)      |
|--------------------|------------------------|-------------------------|
| `commit()` called  | Inside every service   | Only in `get_db`        |
| `rollback()` called| Inside every try/except| Only in `get_db`        |
| Service methods    | try/except + commit    | Pure business logic     |
| Celery tasks       | Manual session + commit| `get_db_context()`      |
| Risk of forgetting | commit or rollback     | None — handled centrally|

---

## Exception Handling

### Domain Exceptions (`app/exceptions.py`)

```python
class InvoiceNotFoundError(Exception):
    """Raised when an invoice cannot be located."""
    pass


class InvalidPaymentError(ValueError):
    """
    Raised when a payment amount is invalid relative
    to the invoice total or current balance.
    """
    pass


class ContractExpiredError(Exception):
    """Raised when acting on an expired contract."""
    pass


class DuplicateWebhookError(Exception):
    """Raised when a webhook event is redelivered."""
    pass
```

### API Layer — Convert to HTTP Exceptions

```python
@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(
        get_invoice_service
    ),
) -> InvoiceResponse:
    """Retrieve a single invoice by its ID."""
    try:
        return service.get_invoice(invoice_id)
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
```

---

## Branding System

NexBill supports per-tenant branding. The default brand
is **NexBill** but every workspace can override it.
Branding is stored in the database and served via a
dedicated settings API. PDF invoices and emails render
using the active brand configuration.

### What Is Configurable

| Field            | Default        | Description                |
|------------------|----------------|----------------------------|
| `brand_name`     | `NexBill`      | Application / company name |
| `logo_url`       | NexBill logo   | S3 URL of uploaded logo    |
| `primary_color`  | `#1A56DB`      | Hex color for UI and PDFs  |
| `accent_color`   | `#7E3AF2`      | Secondary highlight color  |
| `invoice_prefix` | `INV`          | Invoice number prefix      |
| `footer_text`    | NexBill tagline| Footer on PDF invoices     |
| `support_email`  | `null`         | Reply-to on sent invoices  |
| `website`        | `null`         | Shown on invoice footer    |

### Database Model

```python
# app/models/brand_settings.py

from sqlalchemy import Column, Integer, String, Text
from app.infrastructure.database import Base


class BrandSettings(Base):
    """
    Stores workspace-level branding configuration.
    Falls back to NexBill defaults when a field is
    null or not yet customised.
    """

    __tablename__ = "brand_settings"

    id = Column(Integer, primary_key=True)
    brand_name = Column(
        String(100),
        nullable=False,
        default="NexBill",
    )
    logo_url = Column(Text, nullable=True)
    primary_color = Column(
        String(7),
        nullable=False,
        default="#1A56DB",
    )
    accent_color = Column(
        String(7),
        nullable=False,
        default="#7E3AF2",
    )
    invoice_prefix = Column(
        String(10),
        nullable=False,
        default="INV",
    )
    footer_text = Column(Text, nullable=True)
    support_email = Column(
        String(255), nullable=True
    )
    website = Column(String(255), nullable=True)
```

### Pydantic Schemas

```python
# app/schemas/brand_schema.py

from typing import Optional
from pydantic import BaseModel, Field


class BrandSettingsUpdate(BaseModel):
    """
    Schema for updating workspace branding.
    All fields are optional — only provided fields
    will be updated (PATCH semantics).
    """

    brand_name: Optional[str] = Field(
        default=None, max_length=100
    )
    primary_color: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    accent_color: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    invoice_prefix: Optional[str] = Field(
        default=None, max_length=10
    )
    footer_text: Optional[str] = Field(
        default=None, max_length=500
    )
    support_email: Optional[str] = Field(
        default=None, max_length=255
    )
    website: Optional[str] = Field(
        default=None, max_length=255
    )


class BrandSettingsResponse(BaseModel):
    """Schema for brand settings API response."""

    brand_name: str
    logo_url: Optional[str]
    primary_color: str
    accent_color: str
    invoice_prefix: str
    footer_text: Optional[str]
    support_email: Optional[str]
    website: Optional[str]

    class Config:
        from_attributes = True
```

### Repository

```python
# app/repositories/brand_repository.py

from typing import Optional
from sqlalchemy.orm import Session

from app.models.brand_settings import BrandSettings
from app.repositories.base_repository import (
    BaseRepository,
)


class BrandRepository(BaseRepository[BrandSettings]):
    """
    Data access layer for workspace branding config.
    Always operates on a single settings row.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(BrandSettings, db)

    def get_settings(self) -> Optional[BrandSettings]:
        """
        Fetch the current workspace brand config.
        Returns None if not yet initialised.
        """
        return (
            self.db.query(BrandSettings).first()
        )

    def get_or_create_defaults(
        self,
    ) -> BrandSettings:
        """
        Return existing settings or create a default
        NexBill config if none exists yet.
        """
        settings = self.get_settings()
        if settings:
            return settings
        defaults = BrandSettings()
        self.db.add(defaults)
        self.db.flush()
        return defaults
```

### Service

```python
# app/services/brand_service.py

from sqlalchemy.orm import Session

from app.models.brand_settings import BrandSettings
from app.repositories.brand_repository import (
    BrandRepository,
)
from app.schemas.brand_schema import BrandSettingsUpdate
from app.infrastructure.s3_client import S3Client


class BrandService:
    """
    Manages workspace branding configuration.
    Handles logo upload to S3 and settings updates.
    """

    def __init__(
        self,
        db: Session,
        s3: S3Client,
    ) -> None:
        self.db = db
        self.brand_repo = BrandRepository(db)
        self.s3 = s3

    def get_brand(self) -> BrandSettings:
        """
        Return current brand settings, initialising
        NexBill defaults if not yet configured.
        """
        return self.brand_repo.get_or_create_defaults()

    def update_brand(
        self,
        payload: BrandSettingsUpdate,
    ) -> BrandSettings:
        """
        Apply partial brand settings update atomically.

        Args:
            payload: Fields to update (PATCH style).

        Returns:
            Updated BrandSettings instance.
        """
        try:
            brand = (
                self.brand_repo.get_or_create_defaults()
            )
            update_data = payload.model_dump(
                exclude_none=True
            )
            for field, value in update_data.items():
                setattr(brand, field, value)

            self.db.flush()
            self.db.commit()
            self.db.refresh(brand)
            return brand

        except Exception:
            self.db.rollback()
            raise

    def upload_logo(
        self,
        file_bytes: bytes,
        content_type: str,
    ) -> BrandSettings:
        """
        Upload a new logo to S3 and store the URL.

        Args:
            file_bytes: Raw image file content.
            content_type: MIME type (image/png etc.).

        Returns:
            Updated BrandSettings with new logo_url.
        """
        try:
            logo_url = self.s3.upload(
                key="brand/logo",
                data=file_bytes,
                content_type=content_type,
            )
            brand = (
                self.brand_repo.get_or_create_defaults()
            )
            brand.logo_url = logo_url
            self.db.flush()
            self.db.commit()
            self.db.refresh(brand)
            return brand

        except Exception:
            self.db.rollback()
            raise

    def reset_to_defaults(self) -> BrandSettings:
        """
        Reset all branding fields back to the
        NexBill defaults. Logo is not deleted from
        S3 but the URL reference is cleared.

        Returns:
            BrandSettings reset to defaults.
        """
        try:
            brand = (
                self.brand_repo.get_or_create_defaults()
            )
            brand.brand_name = "NexBill"
            brand.logo_url = None
            brand.primary_color = "#1A56DB"
            brand.accent_color = "#7E3AF2"
            brand.invoice_prefix = "INV"
            brand.footer_text = None
            brand.support_email = None
            brand.website = None
            self.db.flush()
            self.db.commit()
            self.db.refresh(brand)
            return brand

        except Exception:
            self.db.rollback()
            raise
```

### API Endpoints

```python
# app/api/v1/brand.py

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from app.schemas.brand_schema import (
    BrandSettingsUpdate,
    BrandSettingsResponse,
)
from app.services.brand_service import BrandService
from app.api.deps import get_current_user, require_admin

router = APIRouter(
    prefix="/brand", tags=["Branding"]
)


@router.get(
    "/",
    response_model=BrandSettingsResponse,
)
def get_brand_settings(
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Return current workspace branding config.
    Accessible to all authenticated users.
    """
    return service.get_brand()


@router.patch(
    "/",
    response_model=BrandSettingsResponse,
    dependencies=[Depends(require_admin)],
)
def update_brand_settings(
    payload: BrandSettingsUpdate,
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Update workspace branding. Admin only.
    Only provided fields are updated.
    """
    return service.update_brand(payload)


@router.post(
    "/logo",
    response_model=BrandSettingsResponse,
    dependencies=[Depends(require_admin)],
)
async def upload_logo(
    file: UploadFile = File(...),
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Upload a new brand logo. Admin only.
    Accepts PNG, JPG, SVG. Max size: 2MB.
    """
    content = await file.read()
    return service.upload_logo(
        file_bytes=content,
        content_type=file.content_type,
    )


@router.post(
    "/reset",
    response_model=BrandSettingsResponse,
    dependencies=[Depends(require_admin)],
)
def reset_brand(
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Reset all branding to NexBill defaults.
    Admin only.
    """
    return service.reset_to_defaults()
```

### Branding in PDF Invoices

The PDF generation service injects brand settings so
every invoice renders with the active logo and colours.

```python
# app/services/pdf_service.py

from app.services.brand_service import BrandService


class PdfService:
    """
    Generates invoice PDFs using the active workspace
    branding (logo, colours, prefix, footer).
    """

    def __init__(
        self,
        brand_service: BrandService,
    ) -> None:
        self.brand = brand_service.get_brand()

    def render_invoice(
        self,
        invoice: Invoice,
    ) -> bytes:
        """
        Render invoice to PDF bytes using active brand.

        Args:
            invoice: Invoice domain model to render.

        Returns:
            PDF file content as bytes.
        """
        context = {
            "brand_name": self.brand.brand_name,
            "logo_url": self.brand.logo_url,
            "primary_color": self.brand.primary_color,
            "footer_text": self.brand.footer_text,
            "invoice_number": (
                f"{self.brand.invoice_prefix}"
                f"-{invoice.id:05d}"
            ),
            "invoice": invoice,
        }
        # Render HTML template and convert to PDF
        return self._html_to_pdf(context)
```

### Branding in Outgoing Emails

```python
# app/services/email_service.py

class EmailService:
    """
    Sends transactional emails using the active brand
    name and reply-to address.
    """

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
            subject=(
                f"Invoice from {brand.brand_name}"
            ),
            template="invoice_email",
            context={"invoice": invoice, "brand": brand},
        )
```

### Brand API Endpoint Summary

| Method | Endpoint       | Access    | Description               |
|--------|----------------|-----------|---------------------------|
| GET    | `/brand/`      | All users | Get current brand config  |
| PATCH  | `/brand/`      | Admin     | Update brand fields       |
| POST   | `/brand/logo`  | Admin     | Upload new logo to S3     |
| POST   | `/brand/reset` | Admin     | Reset to NexBill defaults |

---

## Database Schema

```
users
  id, email, hashed_password, role, created_at

clients
  id, name, tax_id, currency,
  billing_address, created_by (FK → users)

contacts
  id, client_id (FK), name, email, phone

contracts
  id, client_id (FK), start_date, end_date,
  billing_cycle, auto_renew, status

invoices
  id, client_id (FK), contract_id (FK, nullable),
  invoice_number, status, currency,
  total_amount, amount_paid, due_date,
  created_by (FK → users)

invoice_items
  id, invoice_id (FK), description,
  quantity, unit_price, tax_rate, discount

payments
  id, invoice_id (FK), amount, method,
  provider_ref, paid_at

webhook_events
  id, event_id (unique), provider, processed_at

brand_settings
  id, brand_name, logo_url, primary_color,
  accent_color, invoice_prefix, footer_text,
  support_email, website

audit_logs
  id, entity, entity_id, action,
  changed_by (FK → users), changed_at
```

---

## API Endpoint Overview

### Auth
| Method | Endpoint         | Description           |
|--------|------------------|-----------------------|
| POST   | `/auth/register` | Register new user     |
| POST   | `/auth/login`    | Login, receive JWT    |
| POST   | `/auth/refresh`  | Refresh access token  |

### Clients
| Method | Endpoint          | Description         |
|--------|-------------------|---------------------|
| GET    | `/clients/`       | List all clients    |
| POST   | `/clients/`       | Create client       |
| GET    | `/clients/{id}`   | Get client detail   |
| PUT    | `/clients/{id}`   | Update client       |
| DELETE | `/clients/{id}`   | Soft delete client  |

### Invoices
| Method | Endpoint                  | Description       |
|--------|---------------------------|-------------------|
| GET    | `/invoices/`              | List invoices     |
| POST   | `/invoices/`              | Create invoice    |
| GET    | `/invoices/{id}`          | Get invoice       |
| PUT    | `/invoices/{id}`          | Update invoice    |
| POST   | `/invoices/{id}/send`     | Send invoice      |
| POST   | `/invoices/{id}/payments` | Record payment    |
| GET    | `/invoices/{id}/pdf`      | Download PDF      |

### Contracts
| Method | Endpoint                  | Description       |
|--------|---------------------------|-------------------|
| GET    | `/contracts/`             | List contracts    |
| POST   | `/contracts/`             | Create contract   |
| PUT    | `/contracts/{id}`         | Update contract   |
| POST   | `/contracts/{id}/pause`   | Pause contract    |

### Reports
| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| GET    | `/reports/revenue`     | Revenue summary      |
| GET    | `/reports/aging`       | Aging receivables    |
| GET    | `/reports/tax-summary` | Tax summary          |

### Branding
| Method | Endpoint       | Description               |
|--------|----------------|---------------------------|
| GET    | `/brand/`      | Get current brand config  |
| PATCH  | `/brand/`      | Update brand fields       |
| POST   | `/brand/logo`  | Upload logo to S3         |
| POST   | `/brand/reset` | Reset to NexBill defaults |

---

## Testing Strategy

- **Unit tests** — service layer in isolation using
  mocked repositories
- **Integration tests** — repository layer against a
  real test PostgreSQL instance
- **API tests** — route handlers via `httpx.AsyncClient`
- **Target:** 80%+ coverage on service and repository
  layers

```
tests/
├── unit/
│   ├── test_invoice_service.py
│   ├── test_payment_service.py
│   └── test_contract_service.py
├── integration/
│   ├── test_invoice_repository.py
│   └── test_payment_repository.py
└── conftest.py
```
