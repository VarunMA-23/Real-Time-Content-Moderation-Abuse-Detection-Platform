"""
Canonical enum definitions for the ShieldAI moderation system.

These enums serve as the single source of truth for:
- Message status values
- Moderation stage identifiers
- Moderation result decisions
- Reviewer action types
- Reviewer decision types

All database columns use typed enums where possible.
API layers may map these to frontend-compatible values.
"""

from enum import Enum


# Message status - canonical lifecycle state
class MessageStatus(str, Enum):
    ALLOWED = "allowed"
    FLAGGED = "flagged"
    BLOCKED = "blocked"
    PENDING_REVIEW = "pending_review"
    ESCALATED = "escalated"


# Moderation stage - identifies which processing stage produced the result
class ModerationStage(str, Enum):
    FAST_MODEL = "fast_model"
    LLM = "llm"
    IMAGE = "image"


# Moderation result decision - what the moderation system decided
class ModerationDecision(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    HOLD_FOR_REVIEW = "hold_for_review"


# Reviewer decision - how the reviewer responded to the moderation
class ReviewerDecision(str, Enum):
    CONFIRM = "confirm"
    OVERRIDE = "override"
    ESCALATE = "escalate"


# Reviewer action - the specific action taken by reviewer
class ReviewerAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    BAN = "ban"
    ESCALATE = "escalate"


# Content type for messages
class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"


# Ingestion/source channel
class IngestionChannel(str, Enum):
    API = "api"
    WEBHOOK = "webhook"
    USER_UPLOAD = "user_upload"
    BATCH_IMPORT = "batch_import"
