from typing import Any
from fastapi import APIRouter

from app.api import deps
from app.ml.service import ModelService
from app.schemas.message import ModerateRequest, ModerateResponse, JobResponse
from app.repositories import MessagesRepository, ModerationResultsRepository
from app.schemas.enums import ContentType, MessageStatus, ModerationStage, ModerationDecision

router = APIRouter()

@router.post("/moderate", response_model=ModerateResponse)
def moderate_content(
    db: deps.SessionDep,
    body: ModerateRequest,
    current_user: deps.CurrentUser,
) -> Any:
    from app.repositories.policy_configs import PolicyConfigsRepository, DEFAULT_POLICY_RULES
    from app.services.moderation import DEFAULT_POLICY_REGION

    # Fetch dynamic policies for the customer
    policy_repo = PolicyConfigsRepository(db)
    policy = policy_repo.get_current_policy(current_user.id, DEFAULT_POLICY_REGION)
    
    thresholds = {
        "toxicity": policy.get("toxicityThreshold", DEFAULT_POLICY_RULES["toxicityThreshold"]),
        "spam": policy.get("spamThreshold", DEFAULT_POLICY_RULES["spamThreshold"]),
        "selfHarm": policy.get("selfHarmThreshold", DEFAULT_POLICY_RULES["selfHarmThreshold"]),
    }
    flag_factor = 0.7 # Could also be moved to policy config later

    model_service = ModelService()
    scores, latency_ms = model_service.predict_with_latency(body.text)

    risk_score = max(scores.values())
    max_label = max(scores, key=scores.get)
    threshold = thresholds.get(max_label, 0.7)

    if risk_score >= threshold:
        decision = ModerationDecision.BLOCK
        status = MessageStatus.BLOCKED
        frontend_decision = "blocked"
    elif risk_score >= threshold * flag_factor:
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
    # Flush to get ID if needed, but repo.create adds to session. 
    # We commit both at once for atomicity.
    ModerationResultsRepository(db).create(
        message_id=message.id,
        stage=ModerationStage.FAST_MODEL,
        risk_score=risk_score,
        labels=scores,
        decision=decision,
        model_version="multihead-bilstm-v1",
        latency_ms=latency_ms,
    )

    db.commit()
    db.refresh(message)

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
