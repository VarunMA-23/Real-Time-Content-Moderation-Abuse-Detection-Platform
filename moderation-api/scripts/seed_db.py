import logging
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.message import Message
from app.models.moderation_result import ModerationResult
from app.models.reviewer_decision import ReviewerDecision
from app.models.policy_config import PolicyConfig
from app.schemas.enums import (
    MessageStatus,
    ContentType,
    IngestionChannel,
    ModerationStage,
    ModerationDecision,
    ReviewerDecision as ReviewerDecisionEnum,
    ReviewerAction,
)
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    # Create admin user if not exists
    user = db.query(User).filter(User.email == "admin@shieldai.com").first()
    if not user:
        user = User(
            email="admin@shieldai.com",
            hashed_password=get_password_hash("123456"),
            name="Admin User",
            is_superuser=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Admin user created")
    else:
        user.hashed_password = get_password_hash("123456")
        db.commit()
        db.refresh(user)
        logger.info("Admin user already exists")

    # Tie sample data to the seeded admin account so it is visible after login
    customer_id = user.id
    user_id_1 = uuid.UUID("22222222-2222-2222-2222-222222222222")
    user_id_2 = uuid.UUID("33333333-3333-3333-3333-333333333333")
    reviewer_id_1 = uuid.UUID("44444444-4444-4444-4444-444444444444")
    reviewer_id_2 = uuid.UUID("55555555-5555-5555-5555-555555555555")

    # Create sample messages in different statuses
    messages = [
        Message(
            content="Hello everyone! Hope you're having a great day.",
            content_type=ContentType.TEXT,
            customer_id=customer_id,
            user_id=user_id_1,
            status=MessageStatus.ALLOWED,
            source="web",
            ingestion_channel=IngestionChannel.API,
        ),
        Message(
            content="You are all worthless and should just give up.",
            content_type=ContentType.TEXT,
            customer_id=customer_id,
            user_id=user_id_2,
            status=MessageStatus.FLAGGED,
            source="web",
            ingestion_channel=IngestionChannel.WEBHOOK,
        ),
        Message(
            content="I hate myself and want to die.",
            content_type=ContentType.TEXT,
            customer_id=customer_id,
            user_id=user_id_1,
            status=MessageStatus.BLOCKED,
            source="mobile",
            ingestion_channel=IngestionChannel.USER_UPLOAD,
        ),
        Message(
            content="This looks suspicious but I'm not sure.",
            content_type=ContentType.TEXT,
            customer_id=customer_id,
            user_id=user_id_2,
            status=MessageStatus.PENDING_REVIEW,
            source="api",
            ingestion_channel=IngestionChannel.API,
        ),
        Message(
            content="Escalated for human review due to high risk score.",
            content_type=ContentType.TEXT,
            customer_id=customer_id,
            user_id=user_id_1,
            status=MessageStatus.ESCALATED,
            source="web",
            ingestion_channel=IngestionChannel.BATCH_IMPORT,
        ),
    ]

    # Add messages if they don't exist (check by content hash for idempotency)
    for msg in messages:
        existing = db.query(Message).filter(Message.content == msg.content).first()
        if not existing:
            db.add(msg)
    db.commit()

    # Query messages to get their IDs
    msg1 = db.query(Message).filter(Message.content == "Hello everyone! Hope you're having a great day.").first()
    msg2 = db.query(Message).filter(Message.content == "You are all worthless and should just give up.").first()
    msg3 = db.query(Message).filter(Message.content == "I hate myself and want to die.").first()
    msg4 = db.query(Message).filter(Message.content == "This looks suspicious but I'm not sure.").first()
    msg5 = db.query(Message).filter(Message.content == "Escalated for human review due to high risk score.").first()

    # Create moderation results for messages
    moderation_results = [
        # Message 1 - clean content, fast model passed
        ModerationResult(
            message_id=msg1.id if msg1 else uuid.uuid4(),
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.02,
            labels={"hate": 0.01, "threat": 0.01, "self_harm": 0.01},
            decision=ModerationDecision.ALLOW,
            model_version="fast-v1.0.0",
            latency_ms=45,
        ),
        # Message 2 - hate speech detected
        ModerationResult(
            message_id=msg2.id if msg2 else uuid.uuid4(),
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.85,
            labels={"hate": 0.92, "threat": 0.78, "insult": 0.88},
            decision=ModerationDecision.HOLD_FOR_REVIEW,
            model_version="fast-v1.0.0",
            latency_ms=52,
        ),
        ModerationResult(
            message_id=msg2.id if msg2 else uuid.uuid4(),
            stage=ModerationStage.LLM,
            risk_score=0.91,
            labels={"hate": 0.95, "threat": 0.89, "insult": 0.93},
            decision=ModerationDecision.BLOCK,
            model_version="llm-v2.1.0",
            latency_ms=850,
        ),
        # Message 3 - self-harm detected
        ModerationResult(
            message_id=msg3.id if msg3 else uuid.uuid4(),
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.95,
            labels={"self_harm": 0.98, "suicide": 0.94, "depression": 0.89},
            decision=ModerationDecision.HOLD_FOR_REVIEW,
            model_version="fast-v1.0.0",
            latency_ms=48,
        ),
        ModerationResult(
            message_id=msg3.id if msg3 else uuid.uuid4(),
            stage=ModerationStage.LLM,
            risk_score=0.97,
            labels={"self_harm": 0.99, "suicide": 0.97, "anxiety": 0.91},
            decision=ModerationDecision.BLOCK,
            model_version="llm-v2.1.0",
            latency_ms=920,
        ),
        # Message 4 - ambiguous content
        ModerationResult(
            message_id=msg4.id if msg4 else uuid.uuid4(),
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.45,
            labels={"suspicious": 0.45, "spam": 0.30},
            decision=ModerationDecision.HOLD_FOR_REVIEW,
            model_version="fast-v1.0.0",
            latency_ms=50,
        ),
        ModerationResult(
            message_id=msg4.id if msg4 else uuid.uuid4(),
            stage=ModerationStage.LLM,
            risk_score=0.38,
            labels={"suspicious": 0.40, "spam": 0.25, "clarified": 0.75},
            decision=ModerationDecision.ALLOW,
            model_version="llm-v2.1.0",
            latency_ms=780,
        ),
        # Message 5 - escalated content
        ModerationResult(
            message_id=msg5.id if msg5 else uuid.uuid4(),
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.72,
            labels={"threat": 0.68, "harassment": 0.75},
            decision=ModerationDecision.HOLD_FOR_REVIEW,
            model_version="fast-v1.0.0",
            latency_ms=49,
        ),
    ]

    # Add moderation results if not exists
    for result in moderation_results:
        existing = db.query(ModerationResult).filter(
            ModerationResult.message_id == result.message_id,
            ModerationResult.stage == result.stage,
        ).first()
        if not existing:
            db.add(result)
    db.commit()

    # Create reviewer decisions
    reviewer_decisions = [
        ReviewerDecision(
            message_id=msg2.id if msg2 else uuid.uuid4(),
            reviewer_id=reviewer_id_1,
            decision=ReviewerDecisionEnum.CONFIRM,
            action=ReviewerAction.REJECT,
            notes="Confirmed hate speech. Block applied.",
        ),
        ReviewerDecision(
            message_id=msg3.id if msg3 else uuid.uuid4(),
            reviewer_id=reviewer_id_2,
            decision=ReviewerDecisionEnum.OVERRIDE,
            action=ReviewerAction.APPROVE,
            notes="After review, this appears to be a cry for help. User needs support, not blocking.",
        ),
        ReviewerDecision(
            message_id=msg4.id if msg4 else uuid.uuid4(),
            reviewer_id=reviewer_id_1,
            decision=ReviewerDecisionEnum.CONFIRM,
            action=ReviewerAction.APPROVE,
            notes="Ambiguous but not explicit. Allowing with warning.",
        ),
        ReviewerDecision(
            message_id=msg5.id if msg5 else uuid.uuid4(),
            reviewer_id=reviewer_id_2,
            decision=ReviewerDecisionEnum.ESCALATE,
            action=ReviewerAction.ESCALATE,
            notes="High-risk content requiring legal review. Escalated to team lead.",
        ),
    ]

    for decision in reviewer_decisions:
        existing = db.query(ReviewerDecision).filter(
            ReviewerDecision.message_id == decision.message_id,
            ReviewerDecision.reviewer_id == decision.reviewer_id,
        ).first()
        if not existing:
            db.add(decision)
    db.commit()

    # Create policy configs for sample customers/regions
    policy_configs = [
        PolicyConfig(
            customer_id=customer_id,
            region="US",
            rules={
                "toxicityThreshold": 0.7,
                "spamThreshold": 0.8,
                "selfHarmThreshold": 0.6,
                "hateSpeechThreshold": 0.7,
                "autoBlock": True,
                "llmReview": True,
            },
            version=1,
            updated_by=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        ),
        PolicyConfig(
            customer_id=customer_id,
            region="EU",
            rules={
                "toxicityThreshold": 0.65,
                "spamThreshold": 0.75,
                "selfHarmThreshold": 0.55,
                "hateSpeechThreshold": 0.65,
                "autoBlock": True,
                "llmReview": True,
            },
            version=1,
            updated_by=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        ),
        PolicyConfig(
            customer_id=customer_id,
            region="US",
            rules={
                "toxicityThreshold": 0.68,
                "spamThreshold": 0.78,
                "selfHarmThreshold": 0.58,
                "hateSpeechThreshold": 0.68,
                "autoBlock": True,
                "llmReview": True,
            },
            version=2,
            updated_by=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        ),
    ]

    for config in policy_configs:
        existing = db.query(PolicyConfig).filter(
            PolicyConfig.customer_id == config.customer_id,
            PolicyConfig.region == config.region,
            PolicyConfig.version == config.version,
        ).first()
        if not existing:
            db.add(config)
    db.commit()

    logger.info("Sample data created")


def main() -> None:
    logger.info("Initializing database")
    db = SessionLocal()
    init_db(db)
    logger.info("Database initialized")


if __name__ == "__main__":
    main()
