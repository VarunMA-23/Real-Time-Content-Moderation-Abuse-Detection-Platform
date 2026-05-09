"""Authentication helpers shared across API endpoints."""

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.models.user import User


def authenticate_user(
    db: Session,
    email: str,
    password: str,
    invalid_credentials_status: int = status.HTTP_401_UNAUTHORIZED,
) -> User:
    """Validate credentials and return the active user."""
    from sqlalchemy import select
    user = db.scalar(select(User).where(User.email == email))
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=invalid_credentials_status,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def _create_access_token(user_id: object) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return security.create_access_token(user_id, expires_delta=access_token_expires)


def build_login_response(user: User) -> dict:
    """Create the frontend login payload."""
    return {
        "user": user,
        "accessToken": _create_access_token(user.id),
        "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def build_oauth_token_response(user: User) -> dict:
    """Create an OAuth2-compatible bearer token response."""
    return {
        "access_token": _create_access_token(user.id),
        "token_type": "bearer",
    }
