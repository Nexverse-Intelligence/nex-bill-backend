# Standard library
import uuid

# Third-party
from fastapi import APIRouter, Depends, HTTPException, Query, status

# Local
from app.api.deps import CurrentUser, get_client_service
from app.exceptions import ClientNotFoundError
from app.schemas import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
)
from app.services import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("/", response_model=list[ClientResponse])
def list_clients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    search: str | None = Query(default=None),
    service: ClientService = Depends(get_client_service),
    current_user: CurrentUser = None,
) -> list[ClientResponse]:
    """List all active clients."""
    return service.list_clients(skip, limit, search)


@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    payload: ClientCreate,
    service: ClientService = Depends(get_client_service),
    current_user: CurrentUser = None,
) -> ClientResponse:
    """Create a new client."""
    return service.create_client(payload, created_by=current_user.id)


@router.get(
    "/{internal_id}",
    response_model=ClientResponse,
)
def get_client(
    internal_id: uuid.UUID,
    service: ClientService = Depends(get_client_service),
    current_user: CurrentUser = None,
) -> ClientResponse:
    """Retrieve a client by its UUID7 internal_id."""
    try:
        return service.get_client_by_uid(internal_id)
    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.put(
    "/{internal_id}",
    response_model=ClientResponse,
)
def update_client(
    internal_id: uuid.UUID,
    payload: ClientUpdate,
    service: ClientService = Depends(get_client_service),
    current_user: CurrentUser = None,
) -> ClientResponse:
    """Update a client identified by its UUID7."""
    try:
        return service.update_client_by_uid(internal_id, payload)
    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.delete(
    "/{internal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_client(
    internal_id: uuid.UUID,
    service: ClientService = Depends(get_client_service),
    current_user: CurrentUser = None,
) -> None:
    """Soft-delete a client by its UUID7."""
    try:
        service.delete_client_by_uid(internal_id)
    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
