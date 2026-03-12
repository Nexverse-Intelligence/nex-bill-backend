# Standard library
import uuid

# Third-party
from sqlalchemy.orm import Session

# Local
from app.exceptions import ClientNotFoundError
from app.models import Client, Contact
from app.repositories import (
    ClientRepository,
)
from app.schemas import (
    ClientCreate,
    ClientUpdate,
)


class ClientService:
    """
    Manages client and contact lifecycle: create,
    read, update, and soft-delete.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ClientRepository(db)

    def list_clients(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> list[Client]:
        """
        List active clients, optionally filtered.

        Args:
            skip: Records to skip.
            limit: Max records to return.
            search: Optional name substring query.

        Returns:
            List of active Client records.
        """
        if search:
            return self.repo.search_by_name(search)
        return self.repo.get_active(skip, limit)

    def get_client(self, client_id: int) -> Client:
        """
        Fetch a single active client.

        Args:
            client_id: Client primary key.

        Returns:
            Client instance.

        Raises:
            ClientNotFoundError: Client not found.
        """
        client = self.repo.get_by_id(client_id)
        if not client or client.deleted_at:
            raise ClientNotFoundError(f"Client {client_id} not found.")
        return client

    def create_client(
        self,
        payload: ClientCreate,
        created_by: int,
    ) -> Client:
        """
        Create a new client with optional contacts.

        Args:
            payload: Client creation data.
            created_by: ID of the creating user.

        Returns:
            Created Client instance (flushed).
        """
        client = Client(
            name=payload.name,
            tax_id=payload.tax_id,
            currency=payload.currency,
            billing_address=payload.billing_address,
            created_by=created_by,
        )
        self.repo.create(client)

        for contact_data in payload.contacts:
            contact = Contact(
                client_id=client.id,
                **contact_data.model_dump(),
            )
            self.db.add(contact)
        self.db.flush()

        return client

    def update_client(
        self,
        client_id: int,
        payload: ClientUpdate,
    ) -> Client:
        """
        Apply partial update to a client.

        Args:
            client_id: Client primary key.
            payload: Fields to update.

        Returns:
            Updated Client instance.

        Raises:
            ClientNotFoundError: Client not found.
        """
        client = self.get_client(client_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(client, field, value)
        self.db.flush()
        return client

    def delete_client(self, client_id: int) -> None:
        """
        Soft-delete a client.

        Args:
            client_id: Client primary key.

        Raises:
            ClientNotFoundError: Client not found.
        """
        client = self.get_client(client_id)
        self.repo.soft_delete(client)

    def get_client_by_uid(self, internal_id: uuid.UUID) -> Client:
        """Fetch client by UUID7."""
        client = self.repo.get_by_internal_id(internal_id)
        if not client or client.deleted_at:
            raise ClientNotFoundError(f"Client {internal_id} not found.")
        return client

    def update_client_by_uid(
        self, internal_id: uuid.UUID, payload: ClientUpdate
    ) -> Client:
        """Apply partial update to client by UUID7."""
        client = self.get_client_by_uid(internal_id)
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(client, field, value)
        self.db.flush()
        return client

    def delete_client_by_uid(self, internal_id: uuid.UUID) -> None:
        """Soft-delete client by UUID7."""
        client = self.get_client_by_uid(internal_id)
        self.repo.soft_delete(client)
