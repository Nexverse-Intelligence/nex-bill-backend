# Standard library

# Third-party
from fastapi import APIRouter, Depends, HTTPException, status

# Local
from app.api.deps import (
    CurrentUser,
    get_auth_service,
    require_admin,
)
from app.config import settings
from app.exceptions import UnauthorizedError
from app.schemas import (
    InviteResponse,
    PasswordChange,
    PasswordForgot,
    PasswordReset,
    TokenRefresh,
    TokenResponse,
    UserInvite,
    UserLogin,
    UserRegister,
    UserRegisterInvited,
    UserResponse,
)
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user account."""
    try:
        user = service.register(payload)
        return UserResponse.model_validate(user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate and receive a JWT pair."""
    try:
        return service.login(payload.email, payload.password)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: TokenRefresh,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Exchange a refresh token for a new token pair."""
    try:
        return service.refresh(payload.refresh_token)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    user: CurrentUser,
    service: AuthService = Depends(get_auth_service),
) -> None:
    """Change current user password."""
    try:
        service.change_password(user.id, payload)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    payload: PasswordForgot,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    """Request password reset."""
    token = service.forgot_password(payload)
    # In a real app, send email here. Return 200 regardless
    # to prevent enumeration.
    return {
        "message": "If the email exists, a reset link has been sent.",
        "token": (token if settings.DEBUG else None),
    }


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(
    payload: PasswordReset,
    service: AuthService = Depends(get_auth_service),
) -> None:
    """Reset password using token."""
    try:
        service.reset_password(payload)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/invite",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
def invite_user(
    payload: UserInvite,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    """Invite a new user (Admin only)."""
    try:
        token = service.invite_user(payload)
        return {"message": "Invitation sent.", "token": token}
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/register-invited/{token}",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_invited(
    token: str,
    payload: UserRegisterInvited,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Complete registration via invitation."""
    try:
        user = service.register_invited(token, payload.password)
        return UserResponse.model_validate(user)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.get(
    "/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_admin)],
)
def list_users(
    service: AuthService = Depends(get_auth_service),
) -> list[UserResponse]:
    """List all registered users (Admin only)."""
    users = service.list_users()
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/invites",
    response_model=list[InviteResponse],
    dependencies=[Depends(require_admin)],
)
def list_invites(
    service: AuthService = Depends(get_auth_service),
) -> list[InviteResponse]:
    """List all active invitations (Admin only)."""
    return service.list_invites()
