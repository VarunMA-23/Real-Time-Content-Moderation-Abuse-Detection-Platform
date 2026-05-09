"""ReviewerDecisions repository for data access abstraction."""
import uuid
from typing import Optional, List, Dict, Any, Sequence

from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from app.models.reviewer_decision import ReviewerDecision
from app.schemas.enums import ReviewerDecision as DecisionEnum, ReviewerAction
from app.repositories.base import BaseRepository


class ReviewerDecisionsRepository(BaseRepository[ReviewerDecision]):
    """Repository for ReviewerDecision entity operations."""

    def __init__(self, db: Session):
        super().__init__(ReviewerDecision, db)

    def create(self, message_id: uuid.UUID, reviewer_id: uuid.UUID,
               decision: DecisionEnum, action: ReviewerAction,
               notes: Optional[str] = None) -> ReviewerDecision:
        """Create a new reviewer decision (without commit)."""
        decision_record = ReviewerDecision(
            message_id=message_id,
            reviewer_id=reviewer_id,
            decision=decision,
            action=action,
            notes=notes,
        )
        self.db.add(decision_record)
        self.db.flush()
        return decision_record

    def find_by_id(self, decision_id: uuid.UUID) -> Optional[ReviewerDecision]:
        """Retrieve a reviewer decision by ID."""
        return self.get(decision_id)

    def find_by_message(self, message_id: uuid.UUID) -> Sequence[ReviewerDecision]:
        """Get all reviewer decisions for a message (chronological order)."""
        stmt = (
            select(ReviewerDecision)
            .where(ReviewerDecision.message_id == message_id)
            .order_by(ReviewerDecision.created_at.asc())
        )
        return self.db.scalars(stmt).all()

    def find_by_customer_and_date(self, customer_id: uuid.UUID, offset: int = 0, limit: int = 50) -> Sequence[ReviewerDecision]:
        """Get decisions for a customer's messages within date range."""
        from app.models.message import Message

        stmt = (
            select(ReviewerDecision)
            .join(Message, ReviewerDecision.message_id == Message.id)
            .where(Message.customer_id == customer_id)
            .order_by(desc(ReviewerDecision.created_at))
            .offset(offset)
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def get_decision_history(self, message_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get formatted history of all reviewer decisions for a message."""
        decisions = self.find_by_message(message_id)
        return [
            {
                "id": str(d.id),
                "decision": d.decision.value,
                "action": d.action.value,
                "notes": d.notes,
                "reviewer_id": str(d.reviewer_id),
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in decisions
        ]

    def count_by_action(self, action: ReviewerAction) -> int:
        """Count decisions with a specific action."""
        stmt = select(func.count()).select_from(ReviewerDecision).where(ReviewerDecision.action == action)
        return self.db.scalar(stmt) or 0

    def get_reviewer_stats(self, reviewer_id: uuid.UUID) -> Dict[str, Any]:
        """Get statistics for a specific reviewer's decisions."""
        stmt_total = select(func.count()).select_from(ReviewerDecision).where(ReviewerDecision.reviewer_id == reviewer_id)
        total = self.db.scalar(stmt_total) or 0

        stmt_actions = (
            select(ReviewerDecision.action, func.count())
            .where(ReviewerDecision.reviewer_id == reviewer_id)
            .group_by(ReviewerDecision.action)
        )
        action_counts = self.db.execute(stmt_actions).all()
        action_map = {a.value: count for a, count in action_counts}

        stmt_decisions = (
            select(ReviewerDecision.decision, func.count())
            .where(ReviewerDecision.reviewer_id == reviewer_id)
            .group_by(ReviewerDecision.decision)
        )
        decision_counts = self.db.execute(stmt_decisions).all()
        decision_map = {d.value: count for d, count in decision_counts}

        return {
            "total_decisions": total,
            "by_action": action_map,
            "by_decision": decision_map,
        }
