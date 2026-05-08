"""ModerationResults repository for data access abstraction."""
import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from app.models.moderation_result import ModerationResult
from app.schemas.enums import ModerationStage, ModerationDecision


class ModerationResultsRepository:
    """Repository for ModerationResult entity operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, message_id: uuid.UUID, stage: ModerationStage, risk_score: float,
               labels: Dict[str, Any], decision: ModerationDecision, model_version: str,
               latency_ms: Optional[int] = None) -> ModerationResult:
        """Create and persist a new moderation result."""
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
        self.db.commit()
        self.db.refresh(result)
        return result

    def find_by_id(self, result_id: uuid.UUID) -> Optional[ModerationResult]:
        """Retrieve a moderation result by ID."""
        return self.db.query(ModerationResult).filter(ModerationResult.id == result_id).first()

    def find_by_message(self, message_id: uuid.UUID) -> List[ModerationResult]:
        """Get all moderation results for a message (ordered by stage completion)."""
        stmt = (
            select(ModerationResult)
            .where(ModerationResult.message_id == message_id)
            .order_by(ModerationResult.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())

    def find_by_message_and_stage(self, message_id: uuid.UUID, stage: ModerationStage) -> Optional[ModerationResult]:
        """Get a specific stage result for a message."""
        return (
            self.db.query(ModerationResult)
            .filter(
                ModerationResult.message_id == message_id,
                ModerationResult.stage == stage
            )
            .first()
        )

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
        # Count by decision
        decision_counts = (
            self.db.query(ModerationResult.decision, func.count())
            .join(ModerationResult.message)
            .where(ModerationResult.message.customer_id == customer_id)
            .group_by(ModerationResult.decision)
            .all()
        )
        decision_map = {d.value: count for d, count in decision_counts}

        # Average risk score
        avg_risk = self.db.query(func.avg(ModerationResult.risk_score)).scalar() or 0

        # Stage counts
        stage_counts = (
            self.db.query(ModerationResult.stage, func.count())
            .join(ModerationResult.message)
            .where(ModerationResult.message.customer_id == customer_id)
            .group_by(ModerationResult.stage)
            .all()
        )
        stage_map = {s.value: count for s, count in stage_counts}

        return {
            "total_results": sum(decision_map.values()),
            "by_decision": decision_map,
            "by_stage": stage_map,
            "avg_risk_score": round(avg_risk, 4),
        }

    def count_results_by_stage(self, stage: ModerationStage) -> int:
        """Count moderation results for a specific stage."""
        return self.db.query(ModerationResult).filter(ModerationResult.stage == stage).count()
