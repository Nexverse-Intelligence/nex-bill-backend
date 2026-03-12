# Standard library
import os

# Set test DB URL BEFORE any app imports
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Third-party
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

# Local — imported AFTER env var is set
from app.infrastructure.database import Base
from app.models.brand_settings import BrandSettings  # noqa
from app.models.client import Client, Contact  # noqa
from app.models.contract import Contract  # noqa
from app.models.invoice import (  # noqa
    AuditLog,
    Invoice,
    InvoiceItem,
    WebhookEvent,
)
from app.models.payment import Payment  # noqa
from app.models.user import User  # noqa

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create in-memory SQLite engine for tests."""
    e = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
    )

    # SQLite: enable foreign key support
    @event.listens_for(e, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_rec):  # type: ignore
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(e)
    yield e
    Base.metadata.drop_all(e)


@pytest.fixture
def db(engine) -> Session:  # type: ignore[return]
    """
    Provide a test database session.
    Rolls back after each test for isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()
    test_session_maker = sessionmaker(bind=connection)
    session = test_session_maker()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test admin user."""
    user = User(
        email="admin@test.com",
        hashed_password="hashed",
        role="admin",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def test_client(db: Session, test_user: User) -> Client:
    """Create a test client."""
    client = Client(
        name="Acme Corp",
        currency="USD",
        created_by=test_user.id,
    )
    db.add(client)
    db.flush()
    return client
