"""Tests for endpoint service helpers."""

import uuid

from app.models.message import Message
from app.models.moderation_result import ModerationResult
from app.models.user import User
from app.schemas.enums import (
    ContentType,
    MessageStatus,
    ModerationDecision,
    ModerationStage,
    ReviewerAction,
    ReviewerDecision,
)
from app.services.auth import authenticate_user, build_login_response
from app.services.moderation import (
    DEFAULT_MODERATION_SCORES,
    detect_policy_violation,
    normalize_scores,
    resolve_reviewer_outcome,
    serialize_queue_item,
)
from app.core.security import get_password_hash


def test_authenticate_user_returns_active_user(db):
    user = User(
        email="reviewer@shieldai.com",
        hashed_password=get_password_hash("secret123"),
        name="Reviewer",
        is_active=True,
    )
    db.add(user)
    db.commit()

    authenticated = authenticate_user(db, user.email, "secret123")

    assert authenticated.id == user.id


def test_build_login_response_matches_frontend_contract(db):
    user = User(
        email="ops@shieldai.com",
        hashed_password=get_password_hash("secret123"),
        name="Ops User",
        is_active=True,
    )
    db.add(user)
    db.commit()

    payload = build_login_response(user)

    assert payload["user"].id == user.id
    assert payload["accessToken"]
    assert payload["expiresIn"] > 0


def test_normalize_scores_uses_expected_aliases():
    scores = normalize_scores({"hate": 0.8, "spam": 0.3, "self_harm": 0.2})

    assert scores == {"toxicity": 0.8, "spam": 0.3, "selfHarm": 0.2}


def test_detect_policy_violation_ignores_non_numeric_values():
    violation = detect_policy_violation({"category": "hate", "hate_speech": 0.9})

    assert violation == "Hate Speech"


def test_resolve_reviewer_outcome_maps_frontend_actions():
    decision, action, status = resolve_reviewer_outcome("ban")

    assert decision == ReviewerDecision.CONFIRM
    assert action == ReviewerAction.BAN
    assert status == MessageStatus.BLOCKED


def test_serialize_queue_item_builds_frontend_shape(db):
    message = Message(
        content="Potentially harmful content",
        content_type=ContentType.TEXT,
        customer_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status=MessageStatus.FLAGGED,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    latest_result = ModerationResult(
        message_id=message.id,
        stage=ModerationStage.FAST_MODEL,
        risk_score=0.91,
        labels={"hate": 0.91, "spam": 0.1},
        decision=ModerationDecision.HOLD_FOR_REVIEW,
        model_version="fast-v1",
    )

    queue_item = serialize_queue_item(message, latest_result)

    assert queue_item.id == str(message.id)
    assert queue_item.decision == "flagged"
    assert queue_item.scores["toxicity"] == 0.91
    assert queue_item.policyViolation == "Hate"
    assert queue_item.history == []


def test_default_moderation_scores_are_copied():
    first = DEFAULT_MODERATION_SCORES.copy()
    second = DEFAULT_MODERATION_SCORES.copy()
    first["toxicity"] = 1.0

    assert second["toxicity"] == 0.0
