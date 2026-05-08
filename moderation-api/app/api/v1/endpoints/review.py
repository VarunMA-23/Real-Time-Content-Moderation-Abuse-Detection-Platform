import uuid
from typing import Any, Optional
from fastapi import APIRouter, Query

from app.api import deps
from app.repositories import MessagesRepository
from app.repositories.moderation_results import ModerationResultsRepository
from app.schemas.message import QueueResponse, QueueItemResponse
from app.schemas.reviewer_decision import DecisionRequest, DecisionResponse
from app.schemas.enums import (
    MessageStatus,
    ModerationDecision,
    ReviewerDecision,
    ReviewerAction,
)

router = APIRouter()


def to_frontend_decision(latest_decision: ModerationDecision | None, message_status: MessageStatus) -> str:
    if latest_decision == ModerationDecision.BLOCK:
        return "blocked"
    if latest_decision == ModerationDecision.HOLD_FOR_REVIEW:
        return "flagged"
    if latest_decision == ModerationDecision.ALLOW:
        return "allowed"
    return message_status.value


@router.get("/review", response_model=QueueResponse)
def get_review_queue(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
    status: Optional[str] = Query(None),
) -> Any:
    msg_repo = MessagesRepository(db)
    mod_repo = ModerationResultsRepository(db)

    if status:
        try:
            msg_status = MessageStatus(status)
            messages = msg_repo.find_by_status_and_customer(current_user.id, msg_status)
        except ValueError:
            messages = msg_repo.find_flagged_messages_by_customer(current_user.id)
    else:
        messages = msg_repo.find_flagged_messages_by_customer(current_user.id)

    items = []
    for msg in messages:
        latest = mod_repo.get_latest_result_for_message(msg.id)
        decision = to_frontend_decision(latest.decision if latest else None, msg.status)
        labels = latest.labels if latest else {}
        scores = {
            "toxicity": labels.get("toxicity", labels.get("hate", 0)),
            "spam": labels.get("spam", 0),
            "selfHarm": labels.get("self_harm", labels.get("selfHarm", 0)),
        }

        history = []
        for rd in msg.reviewer_decisions:
            history.append({
                "action": rd.action.value,
                "actor": str(rd.reviewer_id),
                "time": rd.created_at.isoformat() if rd.created_at else None,
            })

        violation = None
        if labels:
            for key in labels:
                if labels.get(key, 0) > 0.7:
                    violation = key.replace("_", " ").title()
                    break

        items.append(QueueItemResponse(
            id=str(msg.id),
            text=msg.content,
            userId=str(msg.user_id),
            timestamp=msg.created_at,
            decision=decision,
            scores=scores,
            llmExplanation="Pending LLM analysis.",
            policyViolation=violation,
            history=history,
        ))

    return QueueResponse(queue=items)


@router.post("/decision", response_model=DecisionResponse)
def submit_decision(
    db: deps.SessionDep,
    body: DecisionRequest,
    current_user: deps.CurrentUser,
) -> Any:
    from app.repositories.reviewer_decisions import ReviewerDecisionsRepository
    from app.repositories.messages import MessagesRepository

    msg_repo = MessagesRepository(db)
    dec_repo = ReviewerDecisionsRepository(db)

    message_id = uuid.UUID(body.messageId)

    action_map = {
        "approve": (ReviewerDecision.CONFIRM, ReviewerAction.APPROVE),
        "reject": (ReviewerDecision.CONFIRM, ReviewerAction.REJECT),
        "ban": (ReviewerDecision.CONFIRM, ReviewerAction.BAN),
        "escalate": (ReviewerDecision.ESCALATE, ReviewerAction.ESCALATE),
    }

    rev_decision, rev_action = action_map.get(
        body.action, (ReviewerDecision.CONFIRM, ReviewerAction.APPROVE)
    )

    dec_repo.create(
        message_id=message_id,
        reviewer_id=current_user.id,
        decision=rev_decision,
        action=rev_action,
        notes=None,
    )

    if rev_action == ReviewerAction.REJECT:
        msg_repo.update_status(message_id, MessageStatus.FLAGGED)
    elif rev_action == ReviewerAction.BAN:
        msg_repo.update_status(message_id, MessageStatus.BLOCKED)
    elif rev_action == ReviewerAction.ESCALATE:
        msg_repo.update_status(message_id, MessageStatus.ESCALATED)
    elif rev_action == ReviewerAction.APPROVE:
        msg_repo.update_status(message_id, MessageStatus.ALLOWED)

    return DecisionResponse(success=True)
