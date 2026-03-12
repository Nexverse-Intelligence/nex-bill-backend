# Standard library
import secrets
from datetime import datetime, timedelta

# Third-party
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Local
from app.config import settings
from app.exceptions import UnauthorizedError
from app.infrastructure.redis_client import redis_client
from app.models import User
from app.repositories import (
    UserRepository,
)
from app.schemas import (
    InviteResponse,
    PasswordChange,
    PasswordForgot,
    PasswordReset,
    TokenResponse,
    UserInvite,
    UserRegister,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Handles user registration, login, and JWT
    token issuance and validation.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    # ── Password helpers ──────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        """Hash a plaintext password."""
        return pwd_context.hash(plain)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify plaintext against hashed."""
        return pwd_context.verify(plain, hashed)

    # ── Token helpers ─────────────────────────────

    @staticmethod
    def create_access_token(
        data: dict,
    ) -> str:
        """
        Create a short-lived JWT access token.

        Args:
            data: Claims to encode (must include sub).

        Returns:
            Signed JWT string.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Create a long-lived JWT refresh token.

        Args:
            data: Claims to encode.

        Returns:
            Signed JWT string.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and verify a JWT token.

        Args:
            token: JWT string to decode.

        Returns:
            Decoded payload dict.

        Raises:
            UnauthorizedError: Token invalid/expired.
        """
        try:
            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
        except JWTError as exc:
            raise UnauthorizedError("Invalid or expired token.") from exc

    # ── Domain operations ─────────────────────────

    def register(self, payload: UserRegister) -> User:
        """
        Register a new user account.

        Args:
            payload: Registration data.

        Returns:
            Created User instance (flushed).

        Raises:
            ValueError: Email already in use.
        """
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise ValueError(f"Email {payload.email} already in use.")
        user = User(
            email=payload.email,
            hashed_password=self.hash_password(payload.password),
            role=payload.role,
        )
        return self.user_repo.create(user)

    def login(
        self,
        email: str,
        password: str,
    ) -> TokenResponse:
        """
        Authenticate a user and return token pair.

        Args:
            email: User's email address.
            password: Plaintext password.

        Returns:
            TokenResponse with access and refresh JWTs.

        Raises:
            UnauthorizedError: Credentials invalid.
        """
        user = self.user_repo.get_by_email(email)
        if not user or not self.verify_password(
            password, user.hashed_password
        ):
            raise UnauthorizedError("Invalid email or password.")
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        return TokenResponse(
            access_token=self.create_access_token(payload),
            refresh_token=self.create_refresh_token(payload),
        )

    def refresh(self, refresh_token: str) -> TokenResponse:
        """
        Issue a new token pair from a valid refresh.

        Args:
            refresh_token: Current refresh JWT.

        Returns:
            New TokenResponse.

        Raises:
            UnauthorizedError: Token invalid/expired.
        """
        data = self.decode_token(refresh_token)
        if data.get("type") != "refresh":
            raise UnauthorizedError("Not a refresh token.")
        user_id = int(data["sub"])
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedError("User not found.")
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        return TokenResponse(
            access_token=self.create_access_token(payload),
            refresh_token=self.create_refresh_token(payload),
        )

    def change_password(self, user_id: int, payload: PasswordChange) -> None:
        """
        Change user password.

        Args:
            user_id: ID of the user changing their password.
            payload: Old and new password data.

        Raises:
            UnauthorizedError: Old password verification failed.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user or not self.verify_password(
            payload.old_password, user.hashed_password
        ):
            raise UnauthorizedError("Invalid current password.")

        user.hashed_password = self.hash_password(payload.new_password)
        self.user_repo.db.flush()

    def forgot_password(self, payload: PasswordForgot) -> str:
        """
        Generate a password reset token and store in Redis.

        Args:
            payload: Email of the user who forgot their password.

        Returns:
            The generated reset token.
        """
        user = self.user_repo.get_by_email(payload.email)
        if not user:
            # We return an empty string to avoid leaking email existence,
            # but usually we would just return 200 OK regardless.
            return ""

        token = secrets.token_urlsafe(32)
        # Store token with 1 hour expiration (3600 seconds)
        redis_client.setex(f"reset:{token}", 3600, user.email)
        return token

    def reset_password(self, payload: PasswordReset) -> None:
        """
        Reset password using a token from Redis.

        Args:
            payload: Token and the new password.

        Raises:
            UnauthorizedError: Token invalid or expired.
        """
        email = redis_client.get(f"reset:{payload.token}")
        if not email:
            raise UnauthorizedError("Invalid or expired reset token.")

        user = self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError("User no longer exists.")

        user.hashed_password = self.hash_password(payload.new_password)
        self.user_repo.db.flush()
        redis_client.delete(f"reset:{payload.token}")

    def invite_user(self, payload: UserInvite) -> str:
        """
        Create a user invitation token in Redis.

        Args:
            payload: Email and role for the invitee.

        Returns:
            The generated invitation token.

        Raises:
            ValueError: User already exists.
        """
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise ValueError(
                f"User with email {payload.email} already exists."
            )

        token = secrets.token_urlsafe(32)
        # Store invitation (email and role) with 24 hour expiration
        data = f"{payload.email}:{payload.role}"
        redis_client.setex(f"invite:{token}", 86400, data)
        return token

    def register_invited(self, token: str, password: str) -> User:
        """
        Complete user registration via invitation token.

        Args:
            token: The invitation token.
            password: Password set by the user.

        Returns:
            The created User instance.

        Raises:
            UnauthorizedError: Token invalid or expired.
        """
        data = redis_client.get(f"invite:{token}")
        if not data:
            raise UnauthorizedError("Invalid or expired invitation token.")

        email, role = data.split(":")
        user = User(
            email=email,
            hashed_password=self.hash_password(password),
            role=role,
        )
        new_user = self.user_repo.create(user)
        redis_client.delete(f"invite:{token}")
        return new_user

    def list_users(self) -> list[User]:
        """Fetch all non-deleted users."""
        return self.user_repo.get_all()

    def list_invites(self) -> list[InviteResponse]:
        """Fetch all active invitations from Redis."""
        invites = []
        # In production, scan_iter is safer than keys()
        for key in redis_client.scan_iter("invite:*"):
            token = key.replace("invite:", "")
            data = redis_client.get(key)
            if data:
                email, role = data.split(":")
                ttl = redis_client.ttl(key)
                invites.append(
                    InviteResponse(
                        token=token,
                        email=email,
                        role=role,
                        expires_in=ttl,
                    )
                )
        return invites
