"""Tests for repository layer."""
import uuid

import pytest

from app.models.message import Message
from app.schemas.enums import MessageStatus, ContentType, IngestionChannel
from app.repositories import (
    MessagesRepository,
    ModerationResultsRepository,
    ReviewerDecisionsRepository,
    PolicyConfigsRepository,
)
from app.schemas.enums import ModerationStage, ModerationDecision, ReviewerDecision, ReviewerAction


class TestMessagesRepository:
    """Tests for MessagesRepository."""

    def test_create_message(self, db):
        """Test creating a message through repository."""
        repo = MessagesRepository(db)
        customer_id = uuid.uuid4()
        user_id = uuid.uuid4()

        message = repo.create(
            content="Test message",
            content_type=ContentType.TEXT,
            customer_id=customer_id,
            user_id=user_id,
            status=MessageStatus.ALLOWED,
            source="test",
        )

        assert message.id is not None
        assert message.content == "Test message"
        assert message.customer_id == customer_id

    def test_find_by_id(self, db):
        """Test finding a message by ID."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        repo = MessagesRepository(db)
        found = repo.find_by_id(message.id)

        assert found is not None
        assert found.id == message.id

    def test_find_by_customer(self, db):
        """Test finding messages by customer ID."""
        customer_id = uuid.uuid4()

        for i in range(3):
            message = Message(
                content=f"Message {i}",
                content_type=ContentType.TEXT,
                customer_id=customer_id,
                user_id=uuid.uuid4(),
            )
            db.add(message)
        db.commit()

        repo = MessagesRepository(db)
        messages = repo.find_by_customer(customer_id)

        assert len(messages) == 3

    def test_find_by_status(self, db):
        """Test finding messages by status."""
        for status in [MessageStatus.ALLOWED, MessageStatus.FLAGGED, MessageStatus.BLOCKED]:
            message = Message(
                content=f"Test {status.value}",
                content_type=ContentType.TEXT,
                customer_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                status=status,
            )
            db.add(message)
        db.commit()

        repo = MessagesRepository(db)
        flagged = repo.find_by_status(MessageStatus.FLAGGED)

        assert len(flagged) == 1
        assert flagged[0].status == MessageStatus.FLAGGED

    def test_update_status(self, db):
        """Test updating message status."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            status=MessageStatus.ALLOWED,
        )
        db.add(message)
        db.commit()

        repo = MessagesRepository(db)
        updated = repo.update_status(message.id, MessageStatus.FLAGGED)

        assert updated is not None
        assert updated.status == MessageStatus.FLAGGED


class TestModerationResultsRepository:
    """Tests for ModerationResultsRepository."""

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

        repo = ModerationResultsRepository(db)
        result = repo.create(
            message_id=message.id,
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.85,
            labels={"hate": 0.85},
            decision=ModerationDecision.HOLD_FOR_REVIEW,
            model_version="test-v1",
            latency_ms=45,
        )

        assert result.id is not None
        assert result.message_id == message.id
        assert result.risk_score == 0.85

    def test_find_by_message(self, db):
        """Test getting all results for a message."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        repo = ModerationResultsRepository(db)

        for stage in [ModerationStage.FAST_MODEL, ModerationStage.LLM]:
            result = repo.create(
                message_id=message.id,
                stage=stage,
                risk_score=0.5,
                labels={},
                decision=ModerationDecision.ALLOW,
                model_version="test",
            )
        db.commit()

        results = repo.find_by_message(message.id)

        assert len(results) == 2

    def test_get_latest_result(self, db):
        """Test getting the most recent moderation result."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        repo = ModerationResultsRepository(db)

        # Create results with different timestamps
        result1 = repo.create(
            message_id=message.id,
            stage=ModerationStage.FAST_MODEL,
            risk_score=0.3,
            labels={},
            decision=ModerationDecision.ALLOW,
            model_version="v1",
        )

        # Wait a moment and create another
        import time
        time.sleep(0.01)

        result2 = repo.create(
            message_id=message.id,
            stage=ModerationStage.LLM,
            risk_score=0.4,
            labels={},
            decision=ModerationDecision.ALLOW,
            model_version="v2",
        )

        latest = repo.get_latest_result_for_message(message.id)

        assert latest is not None
        assert latest.id in (result1.id, result2.id)
        results = repo.find_by_message(message.id)
        assert len(results) == 2


class TestReviewerDecisionsRepository:
    """Tests for ReviewerDecisionsRepository."""

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

        repo = ReviewerDecisionsRepository(db)
        decision = repo.create(
            message_id=message.id,
            reviewer_id=uuid.uuid4(),
            decision=ReviewerDecision.CONFIRM,
            action=ReviewerAction.REJECT,
            notes="Test decision",
        )

        assert decision.id is not None
        assert decision.message_id == message.id

    def test_find_by_message(self, db):
        """Test getting decisions for a message."""
        message = Message(
            content="Test",
            content_type=ContentType.TEXT,
            customer_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
        db.add(message)
        db.commit()

        repo = ReviewerDecisionsRepository(db)

        for action in [ReviewerAction.APPROVE, ReviewerAction.REJECT]:
            repo.create(
                message_id=message.id,
                reviewer_id=uuid.uuid4(),
                decision=ReviewerDecision.CONFIRM,
                action=action,
                notes="Test",
            )
        db.commit()

        decisions = repo.find_by_message(message.id)

        assert len(decisions) == 2


class TestPolicyConfigsRepository:
    """Tests for PolicyConfigsRepository."""

    def test_create_policy_config(self, db):
        """Test creating a policy config."""
        repo = PolicyConfigsRepository(db)
        config = repo.create(
            customer_id=uuid.uuid4(),
            region="US",
            rules={"hate_speech": {"threshold": 0.7}},
        )

        assert config.id is not None
        assert config.version == 1

    def test_find_latest_by_customer_and_region(self, db):
        """Test getting latest policy for customer/region."""
        customer_id = uuid.uuid4()

        repo = PolicyConfigsRepository(db)
        v1 = repo.create(customer_id=customer_id, region="US", rules={"v": 1}, updated_by=uuid.uuid4())
        v2 = repo.create(customer_id=customer_id, region="US", rules={"v": 2}, updated_by=uuid.uuid4())

        latest = repo.find_latest_by_customer_and_region(customer_id, "US")

        assert latest.id == v2.id
        assert latest.version == 2

    def test_find_all_versions(self, db):
        """Test getting all policy versions for audit."""
        customer_id = uuid.uuid4()

        repo = PolicyConfigsRepository(db)
        repo.create(customer_id=customer_id, region="EU", rules={"v": 1})
        repo.create(customer_id=customer_id, region="EU", rules={"v": 2})
        repo.create(customer_id=customer_id, region="EU", rules={"v": 3})

        versions = repo.find_all_versions(customer_id, "EU")

        assert len(versions) == 3
        assert versions[0].version == 3
        assert versions[1].version == 2
        assert versions[2].version == 1

    def test_get_current_policy_returns_defaults(self, db):
        """Test that get_current_policy returns defaults when no config exists."""
        repo = PolicyConfigsRepository(db)

        default = repo.get_current_policy(uuid.uuid4(), "US")

        assert "hateSpeechThreshold" in default
        assert "spamThreshold" in default
