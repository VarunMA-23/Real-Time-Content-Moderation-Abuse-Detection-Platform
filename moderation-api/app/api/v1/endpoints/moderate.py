import uuid
from typing import Any
from fastapi import APIRouter

from app.api import deps
from app.schemas.message import ModerateRequest, ModerateResponse, JobResponse
from app.models.message import Message
from app.models.moderation_result import ModerationResult
from app.schemas.enums import ContentType, MessageStatus, ModerationStage, ModerationDecision

router = APIRouter()


@router.post("/moderate", response_model=ModerateResponse)
def moderate_content(
    db: deps.SessionDep,
    body: ModerateRequest,
    current_user: deps.CurrentUser,
) -> Any:
    message = Message(
        content=body.text,
        content_type=ContentType.TEXT,
        customer_id=current_user.id,
        user_id=current_user.id,
        status=MessageStatus.ALLOWED,
        source="api",
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    result = ModerationResult(
        message_id=message.id,
        stage=ModerationStage.FAST_MODEL,
        risk_score=0.0,
        labels={"toxicity": 0.0, "spam": 0.0, "selfHarm": 0.0},
        decision=ModerationDecision.ALLOW,
        model_version="placeholder-v0.1",
        latency_ms=0,
    )
    db.add(result)
    db.commit()

    return ModerateResponse(
        messageId=str(message.id),
        decision="allowed",
        scores={"toxicity": 0.0, "spam": 0.0, "selfHarm": 0.0},
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: str,
    current_user: deps.CurrentUser,
) -> Any:
    return JobResponse(
        status="completed",
        llmExplanation="LLM analysis pending - will be available in future release.",
        policyViolation=None,
    )
