# Standard library
import uuid

# Third-party
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for new user registration."""

    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(default="staff")


class UserLogin(BaseModel):
    """Schema for user login credentials."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for requesting a new access token."""

    refresh_token: str


class UserResponse(BaseModel):
    """
    Schema for returning user data.

    ``internal_id`` is the UUID7 value the frontend
    should use as the canonical identifier. The integer
    ``id`` is never exposed in API responses.
    """

    internal_id: uuid.UUID
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    """Schema for changing password."""

    old_password: str
    new_password: str = Field(min_length=8)


class PasswordForgot(BaseModel):
    """Schema for requesting password reset."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for resetting password with a token."""

    token: str
    new_password: str = Field(min_length=8)


class UserInvite(BaseModel):
    """Schema for inviting a new user."""

    email: EmailStr
    role: str = Field(default="staff")


class UserRegisterInvited(BaseModel):
    """Schema for completing registration via invite token."""

    password: str = Field(min_length=8)


class InviteResponse(BaseModel):
    """Schema for an active user invitation."""

    token: str
    email: str
    role: str
    expires_in: int  # Seconds remaining
