from typing import Any
from fastapi import APIRouter

from app.api import deps
from app.ml.service import ModelService
from app.schemas.message import ModerateRequest, ModerateResponse, JobResponse
from app.repositories import MessagesRepository, ModerationResultsRepository
from app.schemas.enums import ContentType, MessageStatus, ModerationStage, ModerationDecision

router = APIRouter()

_SCORE_THRESHOLDS = {
    "toxicity": 0.7,
    "spam": 0.6,
    "selfHarm": 0.5,
}
_FLAG_FACTOR = 0.7


@router.post("/moderate", response_model=ModerateResponse)
def moderate_content(
    db: deps.SessionDep,
    body: ModerateRequest,
    current_user: deps.CurrentUser,
) -> Any:
    model_service = ModelService()
    scores, latency_ms = model_service.predict_with_latency(body.text)

    risk_score = max(scores.values())
    max_label = max(scores, key=scores.get)
    threshold = _SCORE_THRESHOLDS.get(max_label, 0.7)

    if risk_score >= threshold:
        decision = ModerationDecision.BLOCK
        status = MessageStatus.BLOCKED
        frontend_decision = "blocked"
    elif risk_score >= threshold * _FLAG_FACTOR:
        decision = ModerationDecision.HOLD_FOR_REVIEW
        status = MessageStatus.FLAGGED
        frontend_decision = "flagged"
    else:
        decision = ModerationDecision.ALLOW
        status = MessageStatus.ALLOWED
        frontend_decision = "allowed"

    message = MessagesRepository(db).create(
        content=body.text,
        content_type=ContentType.TEXT,
        customer_id=current_user.id,
        user_id=current_user.id,
        status=status,
        source="api",
    )
    ModerationResultsRepository(db).create(
        message_id=message.id,
        stage=ModerationStage.FAST_MODEL,
        risk_score=risk_score,
        labels=scores,
        decision=decision,
        model_version="multihead-bilstm-v1",
        latency_ms=latency_ms,
    )

    return ModerateResponse(
        messageId=str(message.id),
        decision=frontend_decision,
        scores=scores,
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
