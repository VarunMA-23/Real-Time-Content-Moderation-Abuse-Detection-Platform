"""Tests for database persistence layer."""
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select, desc

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


class TestMessageModel:
    """Tests for the Message model."""

    def test_create_message(self, db):
        """Test creating a new message record."""
        message = Message(
            content="Test message content",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            status=MessageStatus.ALLOWED,
            source="test",
            ingestion_channel=IngestionChannel.API,
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        assert message.id is not None
        assert message.content == "Test message content"
        assert message.content_type == ContentType.TEXT
        assert message.status == MessageStatus.ALLOWED

    def test_message_default_values(self, db):
        """Test message defaults are applied correctly."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        assert message.status == MessageStatus.ALLOWED
        assert message.content_type == ContentType.TEXT

    def test_message_relationships(self, db):
        """Test message relationships with moderation results and reviewer decisions."""
        message = Message(
            content="Test message",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            status=MessageStatus.FLAGGED,
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        # Create moderation result
        result = ModerationResult(
            message_id=message.id,
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.85,
            labels={"hate": 0.85},
            decision=ModerationDecision.HOLD_FOR_REVIEW,
            model_version="test-v1",
        )
        db.add(result)
        db.commit()

        # Reload message to test relationship
        db.refresh(message)
        assert len(message.moderation_results) == 1
        assert message.moderation_results[0].stage == ModerationStage.FAST_MODEL


class TestModerationResultModel:
    """Tests for the ModerationResult model."""

    def test_create_moderation_result(self, db):
        """Test creating a moderation result."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        result = ModerationResult(
            message_id=message.id,
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.45,
            labels={"spam": 0.45},
            decision=ModerationDecision.ALLOW,
            model_version="fast-v1.0",
            latency_ms=50,
        )
        db.add(result)
        db.commit()
        db.refresh(result)

        assert result.id is not None
        assert result.risk_score == 0.45
        assert result.labels == {"spam": 0.45}

    def test_moderation_result_cascade_delete(self, db):
        """Test that moderation results are deleted when message is deleted."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        result = ModerationResult(
            message_id=message.id,
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.1,
            labels={},
            decision=ModerationDecision.ALLOW,
            model_version="test",
        )
        db.add(result)
        db.commit()

        db.delete(message)
        db.commit()

        # Verify result was cascade deleted
        stmt = select(ModerationResult).where(ModerationResult.id == result.id)
        deleted_result = db.scalar(stmt)
        assert deleted_result is None


class TestReviewerDecisionModel:
    """Tests for the ReviewerDecision model."""

    def test_create_reviewer_decision(self, db):
        """Test creating a reviewer decision."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        decision = ReviewerDecision(
            message_id=message.id,
            reviewer_id=uuid.uuid4(),
            decision=ReviewerDecisionEnum.CONFIRM,
            action=ReviewerAction.REJECT,
            notes="Confirmed block decision",
        )
        db.add(decision)
        db.commit()
        db.refresh(decision)

        assert decision.id is not None
        assert decision.decision == ReviewerDecisionEnum.CONFIRM
        assert decision.action == ReviewerAction.REJECT

    def test_reviewer_decision_audit_trail(self, db):
        """Test that multiple decisions can be appended for same message."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        for i, action in enumerate([ReviewerAction.APPROVE, ReviewerAction.REJECT, ReviewerAction.ESCALATE]):
            decision = ReviewerDecision(
                message_id=message.id,
                reviewer_id=uuid.uuid4(),
                decision=ReviewerDecisionEnum.CONFIRM,
                action=action,
                notes=f"Decision #{i+1}",
            )
            db.add(decision)
        db.commit()

        stmt = select(ReviewerDecision).where(
            ReviewerDecision.message_id == message.id
        ).order_by(ReviewerDecision.created_at.asc())
        decisions = list(db.scalars(stmt).all())

        assert len(decisions) == 3
        assert decisions[0].action == ReviewerAction.APPROVE
        assert decisions[1].action == ReviewerAction.REJECT
        assert decisions[2].action == ReviewerAction.ESCALATE


class TestPolicyConfigModel:
    """Tests for the PolicyConfig model."""

    def test_create_policy_config(self, db):
        """Test creating a policy configuration."""
        config = PolicyConfig(
            customer_id=uuid.uuid4(),
            region="US",
            rules={"hate_speech": {"threshold": 0.7}, "spam": {"threshold": 0.6}},
            version=1,
        )
        db.add(config)
        db.commit()
        db.refresh(config)

        assert config.id is not None
        assert config.customer_id is not None
        assert config.region == "US"
        assert config.version == 1

    def test_policy_config_versioning(self, db):
        """Test append-only versioning strategy."""
        customer_id = uuid.uuid4()

        # Create version 1
        config1 = PolicyConfig(
            customer_id=customer_id,
            region="US",
            rules={"threshold": 0.7},
            version=1,
        )
        db.add(config1)
        db.commit()

        # Create version 2
        config2 = PolicyConfig(
            customer_id=customer_id,
            region="US",
            rules={"threshold": 0.6},
            version=2,
        )
        db.add(config2)
        db.commit()

        # Both versions should exist
        stmt = select(PolicyConfig).where(
            PolicyConfig.customer_id == customer_id,
            PolicyConfig.region == "US"
        ).order_by(desc(PolicyConfig.version))
        configs = list(db.scalars(stmt).all())

        assert len(configs) == 2
        assert configs[0].version == 2
        assert configs[1].version == 1

    def test_unique_constraint_on_policy_version(self, db):
        """Test that unique constraint prevents duplicate version."""
        customer_id = uuid.uuid4()

        config = PolicyConfig(
            customer_id=customer_id,
            region="EU",
            rules={},
            version=1,
        )
        db.add(config)
        db.commit()

        # Try to create duplicate (same customer_id, region, version)
        duplicate = PolicyConfig(
            customer_id=customer_id,
            region="EU",
            rules={},
            version=1,
        )
        db.add(duplicate)

        with pytest.raises(Exception):
            db.commit()


class TestCompositeIndexes:
    """Tests for database indexes and query performance."""

    def test_message_by_customer_and_created_at(self, db):
        """Test querying messages by customer with ordering."""
        customer_id = uuid.uuid4()

        # Create multiple messages
        for i in range(5):
            message = Message(
                content=f"Message {i}",
                content_type=ContentType.TEXT,
                customer_id=customer_id,
                user_id=uuid.uuid4(),
                created_at=datetime.utcnow() - timedelta(hours=i),
            )
            db.add(message)
        db.commit()

        # Query with proper ordering
        stmt = (
            select(Message)
            .where(Message.customer_id == customer_id)
            .order_by(desc(Message.created_at))
            .limit(10)
        )
        messages = list(db.scalars(stmt).all())

        assert len(messages) == 5
        # Messages should be ordered by created_at descending
        for i in range(len(messages) - 1):
            assert messages[i].created_at >= messages[i + 1].created_at
