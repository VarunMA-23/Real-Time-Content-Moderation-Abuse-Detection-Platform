"""ModerationResult model for storing stage-by-stage moderation decisions."""
import uuid
from datetime import datetime
from sqlalchemy import String, Double, Integer, DateTime, func, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.schemas.enums import ModerationStage, ModerationDecision


class ModerationResult(Base):
    """Stores moderation decision from a specific stage (fast_model, llm, image)."""

    __tablename__ = "moderation_results"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage: Mapped[ModerationStage] = mapped_column(
        Enum(ModerationStage, name="moderation_stage"),
        nullable=False,
        index=True,
    )
    risk_score: Mapped[float] = mapped_column(Double, nullable=False)
    labels: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    decision: Mapped[ModerationDecision] = mapped_column(
        Enum(ModerationDecision, name="moderation_decision"),
        nullable=False,
        index=True,
    )
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    message: Mapped["Message"] = relationship(
        back_populates="moderation_results",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return (
            f"<ModerationResult(id={self.id}, "
            f"message_id={self.message_id}, "
            f"stage={self.stage.value}, "
            f"decision={self.decision.value})>"
        )
