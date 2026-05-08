"""Moderation and review helpers shared across endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.models.message import Message
from app.models.moderation_result import ModerationResult
from app.schemas.enums import (
    MessageStatus,
    ModerationDecision,
    ReviewerAction,
    ReviewerDecision,
)
from app.schemas.message import QueueItemResponse

DEFAULT_POLICY_REGION = "US"
DEFAULT_MODERATION_SCORES = {
    "toxicity": 0.0,
    "spam": 0.0,
    "selfHarm": 0.0,
}

REVIEW_ACTION_MAP: dict[str, tuple[ReviewerDecision, ReviewerAction, MessageStatus]] = {
    "approve": (ReviewerDecision.CONFIRM, ReviewerAction.APPROVE, MessageStatus.ALLOWED),
    "reject": (ReviewerDecision.CONFIRM, ReviewerAction.REJECT, MessageStatus.FLAGGED),
    "ban": (ReviewerDecision.CONFIRM, ReviewerAction.BAN, MessageStatus.BLOCKED),
    "escalate": (ReviewerDecision.ESCALATE, ReviewerAction.ESCALATE, MessageStatus.ESCALATED),
}


def to_frontend_decision(
    latest_decision: ModerationDecision | None,
    message_status: MessageStatus,
) -> str:
    """Map backend decisions and statuses to frontend labels."""
    if latest_decision == ModerationDecision.BLOCK:
        return "blocked"
    if latest_decision == ModerationDecision.HOLD_FOR_REVIEW:
        return "flagged"
    if latest_decision == ModerationDecision.ALLOW:
        return "allowed"
    return message_status.value


def normalize_scores(labels: Mapping[str, Any] | None) -> dict[str, float]:
    """Normalize stored labels to the frontend score contract."""
    if not labels:
        return DEFAULT_MODERATION_SCORES.copy()
    return {
        "toxicity": float(labels.get("toxicity", labels.get("hate", 0.0))),
        "spam": float(labels.get("spam", 0.0)),
        "selfHarm": float(labels.get("self_harm", labels.get("selfHarm", 0.0))),
    }


def detect_policy_violation(labels: Mapping[str, Any] | None, threshold: float = 0.7) -> str | None:
    """Pick the first label above the violation threshold."""
    if not labels:
        return None
    for key, value in labels.items():
        if isinstance(value, (int, float)) and value > threshold:
            return key.replace("_", " ").title()
    return None


def serialize_history(message: Message) -> list[dict[str, Any]]:
    """Format reviewer decisions for queue responses."""
    return [
        {
            "action": decision.action.value,
            "actor": str(decision.reviewer_id),
            "time": decision.created_at.isoformat() if decision.created_at else None,
        }
        for decision in message.reviewer_decisions
    ]


def serialize_queue_item(message: Message, latest_result: ModerationResult | None) -> QueueItemResponse:
    """Convert a message and latest moderation result into the frontend queue shape."""
    labels = latest_result.labels if latest_result else {}
    return QueueItemResponse(
        id=str(message.id),
        text=message.content,
        userId=str(message.user_id),
        timestamp=message.created_at,
        decision=to_frontend_decision(latest_result.decision if latest_result else None, message.status),
        scores=normalize_scores(labels),
        llmExplanation="Pending LLM analysis.",
        policyViolation=detect_policy_violation(labels),
        history=serialize_history(message),
    )


def resolve_reviewer_outcome(action: str) -> tuple[ReviewerDecision, ReviewerAction, MessageStatus]:
    """Resolve a frontend review action to persisted reviewer and message states."""
    return REVIEW_ACTION_MAP.get(
        action,
        (ReviewerDecision.CONFIRM, ReviewerAction.APPROVE, MessageStatus.ALLOWED),
    )
