"""ReviewerDecision model for storing reviewer actions and decisions."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.schemas.enums import ReviewerDecision, ReviewerAction


class ReviewerDecision(Base):
    """Stores reviewer action taken on a message (append-only audit trail)."""

    __tablename__ = "reviewer_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    decision: Mapped[ReviewerDecision] = mapped_column(
        Enum(ReviewerDecision, name="reviewer_decision"),
        nullable=False,
    )
    action: Mapped[ReviewerAction] = mapped_column(
        Enum(ReviewerAction, name="reviewer_action"),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    message: Mapped["Message"] = relationship(
        back_populates="reviewer_decisions",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<ReviewerDecision(id={self.id}, "
            f"message_id={self.message_id}, "
            f"action={self.action.value})>"
        )
