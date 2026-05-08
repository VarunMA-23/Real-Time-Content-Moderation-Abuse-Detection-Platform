"""Message model for storing moderated content."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.schemas.enums import MessageStatus, ContentType, IngestionChannel


class Message(Base):
    """Stores the moderated content with its lifecycle status."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType, name="content_type"),
        nullable=False,
        default=ContentType.TEXT,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus, name="message_status"),
        nullable=False,
        default=MessageStatus.ALLOWED,
    )
    source: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=None, doc="Ingestion source channel"
    )
    ingestion_channel: Mapped[IngestionChannel | None] = mapped_column(
        Enum(IngestionChannel, name="ingestion_channel"),
        nullable=True,
        default=None,
        doc="Channel through which content was ingested",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    moderation_results: Mapped[list["ModerationResult"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        order_by="ModerationResult.created_at.desc()",
    )
    reviewer_decisions: Mapped[list["ReviewerDecision"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        order_by="ReviewerDecision.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, status={self.status.value})>"
