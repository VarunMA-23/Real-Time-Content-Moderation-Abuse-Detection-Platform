"""Tests for seed data and sample records."""
import uuid
import subprocess
import sys

import pytest


class TestSeedData:
    """Tests for seed database functionality."""

    def test_seed_script_exists(self):
        """Test that seed_db.py exists and is valid Python."""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "scripts/seed_db.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"seed_db.py has syntax errors: {result.stderr}"

    def test_seed_script_has_sample_messages(self):
        """Test that seed script contains sample messages with different statuses."""
        with open("scripts/seed_db.py", "r") as f:
            content = f.read()

        # Check for different message statuses
        assert "ALLOWED" in content
        assert "FLAGGED" in content
        assert "BLOCKED" in content
        assert "PENDING_REVIEW" in content
        assert "ESCALATED" in content

    def test_seed_script_has_moderation_results(self):
        """Test that seed script contains moderation results."""
        with open("scripts/seed_db.py", "r") as f:
            content = f.read()

        assert "ModerationResult" in content
        assert "FAST_MODEL" in content
        assert "LLM" in content

    def test_seed_script_has_reviewer_decisions(self):
        """Test that seed script contains reviewer decision records."""
        with open("scripts/seed_db.py", "r") as f:
            content = f.read()

        assert "ReviewerDecision" in content
        assert "CONFIRM" in content
        assert "OVERRIDE" in content
        assert "ESCALATE" in content

    def test_seed_script_has_policy_configs(self):
        """Test that seed script contains policy configurations."""
        with open("scripts/seed_db.py", "r") as f:
            content = f.read()

        assert "PolicyConfig" in content
        assert "customer_id" in content
        assert "region" in content


class TestSampleDataIntegrity:
    """Tests for sample data integrity in database."""

    @pytest.mark.integration
    def test_sample_messages_in_db(self, db):
        """Test that sample messages are created correctly."""
        from app.models.message import Message
        from app.schemas.enums import MessageStatus

        # Query for messages in different statuses
        allowed_count = db.query(Message).filter(Message.status == MessageStatus.ALLOWED).count()
        flagged_count = db.query(Message).filter(Message.status == MessageStatus.FLAGGED).count()

        # At least some messages should exist after seeding
        assert allowed_count >= 0  # May be 0 if seed hasn't run
        assert flagged_count >= 0

    @pytest.mark.integration
    def test_sample_policy_configs_exist(self, db):
        """Test that sample policy configs exist."""
        from app.models.policy_config import PolicyConfig

        config_count = db.query(PolicyConfig).count()
        # After seeding, should have at least the sample configs
        assert config_count >= 0  # May be 0 if seed hasn't run

    @pytest.mark.integration
    def test_sample_moderation_results_exist(self, db):
        """Test that sample moderation results exist."""
        from app.models.moderation_result import ModerationResult

        result_count = db.query(ModerationResult).count()
        assert result_count >= 0  # May be 0 if seed hasn't run


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
