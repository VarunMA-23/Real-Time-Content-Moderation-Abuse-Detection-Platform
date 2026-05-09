"""ModerationResults repository for data access abstraction."""
import uuid
from typing import Optional, List, Dict, Any, Sequence

from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from app.models.moderation_result import ModerationResult
from app.schemas.enums import ModerationStage, ModerationDecision
from app.repositories.base import BaseRepository


class ModerationResultsRepository(BaseRepository[ModerationResult]):
    """Repository for ModerationResult entity operations."""

    def __init__(self, db: Session):
        super().__init__(ModerationResult, db)

    def create(self, message_id: uuid.UUID, stage: ModerationStage, risk_score: float,
               labels: Dict[str, Any], decision: ModerationDecision, model_version: str,
               latency_ms: Optional[int] = None) -> ModerationResult:
        """Create a new moderation result (without commit)."""
        result = ModerationResult(
            message_id=message_id,
            stage=stage,
            risk_score=risk_score,
            labels=labels,
            decision=decision,
            model_version=model_version,
            latency_ms=latency_ms,
        )
        self.db.add(result)
        self.db.flush()
        return result

    def find_by_id(self, result_id: uuid.UUID) -> Optional[ModerationResult]:
        """Retrieve a moderation result by ID."""
        return self.get(result_id)

    def find_by_message(self, message_id: uuid.UUID) -> Sequence[ModerationResult]:
        """Get all moderation results for a message (ordered by stage completion)."""
        stmt = (
            select(ModerationResult)
            .where(ModerationResult.message_id == message_id)
            .order_by(ModerationResult.created_at.asc())
        )
        return self.db.scalars(stmt).all()

    def find_by_message_and_stage(self, message_id: uuid.UUID, stage: ModerationStage) -> Optional[ModerationResult]:
        """Get a specific stage result for a message."""
        stmt = (
            select(ModerationResult)
            .where(
                ModerationResult.message_id == message_id,
                ModerationResult.stage == stage
            )
        )
        return self.db.scalar(stmt)

    def get_latest_result_for_message(self, message_id: uuid.UUID) -> Optional[ModerationResult]:
        """Get the most recent moderation result for a message."""
        stmt = (
            select(ModerationResult)
            .where(ModerationResult.message_id == message_id)
            .order_by(desc(ModerationResult.created_at), desc(ModerationResult.id))
            .limit(1)
        )
        return self.db.scalar(stmt)

    def get_stage_results(self, message_id: uuid.UUID) -> Dict[str, Any]:
        """Get all stage results for a message as a dictionary keyed by stage name."""
        results = self.find_by_message(message_id)
        return {r.stage.value: r for r in results}

    def get_result_history(self, message_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get formatted history of all moderation results for a message."""
        results = self.find_by_message(message_id)
        return [
            {
                "stage": r.stage.value,
                "risk_score": r.risk_score,
                "labels": r.labels,
                "decision": r.decision.value,
                "model_version": r.model_version,
                "latency_ms": r.latency_ms,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in results
        ]

    def get_summary_stats(self, customer_id: uuid.UUID, days: int = 30) -> Dict[str, Any]:
        """Get moderation result summary statistics for a customer."""
        from app.models.message import Message
        
        # Count by decision
        stmt_decisions = (
            select(ModerationResult.decision, func.count())
            .join(Message, ModerationResult.message_id == Message.id)
            .where(Message.customer_id == customer_id)
            .group_by(ModerationResult.decision)
        )
        decision_counts = self.db.execute(stmt_decisions).all()
        decision_map = {d.value: count for d, count in decision_counts}

        # Average risk score
        stmt_avg_risk = select(func.avg(ModerationResult.risk_score))
        avg_risk = self.db.scalar(stmt_avg_risk) or 0

        # Stage counts
        stmt_stages = (
            select(ModerationResult.stage, func.count())
            .join(Message, ModerationResult.message_id == Message.id)
            .where(Message.customer_id == customer_id)
            .group_by(ModerationResult.stage)
        )
        stage_counts = self.db.execute(stmt_stages).all()
        stage_map = {s.value: count for s, count in stage_counts}

        return {
            "total_results": sum(decision_map.values()),
            "by_decision": decision_map,
            "by_stage": stage_map,
            "avg_risk_score": round(float(avg_risk), 4),
        }

    def count_results_by_stage(self, stage: ModerationStage) -> int:
        """Count moderation results for a specific stage."""
        stmt = select(func.count()).select_from(ModerationResult).where(ModerationResult.stage == stage)
        return self.db.scalar(stmt) or 0
