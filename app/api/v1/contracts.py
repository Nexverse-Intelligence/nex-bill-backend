# Standard library
import uuid

# Third-party
from fastapi import APIRouter, Depends, HTTPException, status

# Local
from app.api.deps import CurrentUser, get_contract_service
from app.exceptions import (
    ContractExpiredError,
    ContractNotFoundError,
)
from app.schemas import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)
from app.services import ContractService

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get("/", response_model=list[ContractResponse])
def list_contracts(
    skip: int = 0,
    limit: int = 100,
    service: ContractService = Depends(get_contract_service),
    current_user: CurrentUser = None,
) -> list[ContractResponse]:
    """List all contracts."""
    return service.list_contracts(skip, limit)


@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    payload: ContractCreate,
    service: ContractService = Depends(get_contract_service),
    current_user: CurrentUser = None,
) -> ContractResponse:
    """Create a new contract."""
    return service.create_contract(payload)


@router.put(
    "/{internal_id}",
    response_model=ContractResponse,
)
def update_contract(
    internal_id: uuid.UUID,
    payload: ContractUpdate,
    service: ContractService = Depends(get_contract_service),
    current_user: CurrentUser = None,
) -> ContractResponse:
    """Update a contract by its UUID7."""
    try:
        return service.update_contract_by_uid(internal_id, payload)
    except ContractNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{internal_id}/pause",
    response_model=ContractResponse,
)
def pause_contract(
    internal_id: uuid.UUID,
    service: ContractService = Depends(get_contract_service),
    current_user: CurrentUser = None,
) -> ContractResponse:
    """Pause an active contract by its UUID7."""
    try:
        return service.pause_contract_by_uid(internal_id)
    except ContractNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except ContractExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post(
    "/{internal_id}/cancel",
    response_model=ContractResponse,
)
def cancel_contract(
    internal_id: uuid.UUID,
    service: ContractService = Depends(get_contract_service),
    current_user: CurrentUser = None,
) -> ContractResponse:
    """Cancel a contract and void pending invoices."""
    try:
        return service.cancel_contract_by_uid(internal_id)
    except ContractNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except ContractExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
