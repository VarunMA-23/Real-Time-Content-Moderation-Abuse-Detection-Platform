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
)
from app.services.moderation import resolve_reviewer_outcome, serialize_queue_item

router = APIRouter()


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

    items = [serialize_queue_item(msg, mod_repo.get_latest_result_for_message(msg.id)) for msg in messages]

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
    rev_decision, rev_action, next_status = resolve_reviewer_outcome(body.action)

    dec_repo.create(
        message_id=message_id,
        reviewer_id=current_user.id,
        decision=rev_decision,
        action=rev_action,
        notes=None,
    )
    msg_repo.update_status(message_id, next_status)
    
    db.commit()

    return DecisionResponse(success=True)
