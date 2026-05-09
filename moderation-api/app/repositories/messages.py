"""Messages repository for data access abstraction."""
import uuid
from typing import Optional, List, Sequence
from datetime import datetime

from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.enums import MessageStatus
from app.repositories.base import BaseRepository


class MessagesRepository(BaseRepository[Message]):
    """Repository for Message entity operations."""

    def __init__(self, db: Session):
        super().__init__(Message, db)

    def create(self, content: str, content_type: str, customer_id: uuid.UUID, user_id: uuid.UUID,
               status: MessageStatus = MessageStatus.ALLOWED, source: Optional[str] = None) -> Message:
        """Create a new message record (without commit)."""
        message = Message(
            content=content,
            content_type=content_type,
            customer_id=customer_id,
            user_id=user_id,
            status=status,
            source=source,
        )
        self.db.add(message)
        self.db.flush()
        return message

    def find_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        """Retrieve a message by its ID."""
        return self.get(message_id)

    def find_by_customer(self, customer_id: uuid.UUID, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        """Find messages by customer ID with pagination."""
        stmt = (
            select(Message)
            .where(Message.customer_id == customer_id)
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def find_by_user(self, user_id: uuid.UUID, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        """Find messages by user ID with pagination."""
        stmt = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def find_by_status(self, status: MessageStatus, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        """Find messages by status (useful for review queue)."""
        stmt = (
            select(Message)
            .where(Message.status == status)
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def find_by_status_and_customer(self, customer_id: uuid.UUID, status: MessageStatus,
                                     offset: int = 0, limit: int = 50) -> Sequence[Message]:
        """Find messages by customer and status (for customer-specific review queue)."""
        stmt = (
            select(Message)
            .where(Message.customer_id == customer_id, Message.status == status)
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def find_flagged_messages(self, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        """Find messages that need review (flagged or blocked)."""
        stmt = (
            select(Message)
            .where(Message.status.in_([MessageStatus.FLAGGED, MessageStatus.BLOCKED]))
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def find_flagged_messages_by_customer(self, customer_id: uuid.UUID, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        """Find flagged or blocked messages for a specific customer."""
        stmt = (
            select(Message)
            .where(
                Message.customer_id == customer_id,
                Message.status.in_([MessageStatus.FLAGGED, MessageStatus.BLOCKED]),
            )
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def update_status(self, message_id: uuid.UUID, status: MessageStatus) -> Optional[Message]:
        """Update message status (without commit)."""
        message = self.find_by_id(message_id)
        if not message:
            return None
        message.status = status
        self.db.add(message)
        self.db.flush()
        return message

    def count_by_status(self, status: MessageStatus) -> int:
        """Count messages with a specific status."""
        stmt = select(func.count()).select_from(Message).where(Message.status == status)
        return self.db.scalar(stmt) or 0

    def count_by_status_for_customer(self, customer_id: uuid.UUID, status: MessageStatus) -> int:
        """Count messages with a specific status for a customer."""
        stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.customer_id == customer_id, Message.status == status)
        )
        return self.db.scalar(stmt) or 0

    def count_by_customer(self, customer_id: uuid.UUID) -> int:
        """Count all messages for a customer."""
        stmt = select(func.count()).select_from(Message).where(Message.customer_id == customer_id)
        return self.db.scalar(stmt) or 0

    def get_queue_stats(self, customer_id: uuid.UUID) -> dict:
        """Get queue statistics for a customer."""
        stats = {
            "pending_review": 0,
            "flagged": 0,
            "blocked": 0,
            "escalated": 0,
            "total": 0,
        }

        for status in MessageStatus:
            count = self.count_by_status_for_customer(customer_id, status)
            stats[status.value] = count
            stats["total"] += count

        return stats
