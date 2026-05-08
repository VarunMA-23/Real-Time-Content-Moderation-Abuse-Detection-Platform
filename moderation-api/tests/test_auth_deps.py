"""Tests for authentication dependencies."""
import uuid

import pytest
from fastapi import HTTPException

from app.api.deps import get_current_user
from app.core.security import create_access_token, get_password_hash
from app.models.user import User


class TestAuthDeps:
    """Regression tests for JWT-backed user resolution."""

    def test_get_current_user_accepts_uuid_subject_string(self, db):
        user = User(
            id=uuid.uuid4(),
            email="admin@shieldai.com",
            hashed_password=get_password_hash("123456"),
            name="Admin User",
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        db.commit()

        token = create_access_token(str(user.id))

        current_user = get_current_user(db, token)

        assert current_user.id == user.id
        assert current_user.email == user.email

    def test_get_current_user_rejects_invalid_uuid_subject(self, db):
        token = create_access_token("not-a-uuid")

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(db, token)

        assert exc_info.value.status_code == 403
