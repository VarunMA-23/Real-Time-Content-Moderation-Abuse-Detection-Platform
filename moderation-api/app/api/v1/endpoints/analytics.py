from typing import Any, Optional
from fastapi import APIRouter, Query

from app.api import deps
from app.repositories.messages import MessagesRepository
from app.schemas.common import AnalyticsResponse, AnalyticsTotals, TimelinePoint, PerformanceMetric
from app.schemas.enums import MessageStatus

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
) -> Any:
    msg_repo = MessagesRepository(db)
    total = msg_repo.count_by_customer(current_user.id)
    blocked = msg_repo.count_by_status_for_customer(current_user.id, MessageStatus.BLOCKED)
    flagged = msg_repo.count_by_status_for_customer(current_user.id, MessageStatus.FLAGGED)

    blocked_pct = round((blocked / total * 100), 1) if total > 0 else 0
    flagged_pct = round((flagged / total * 100), 1) if total > 0 else 0

    return AnalyticsResponse(
        totals=AnalyticsTotals(
            totalMessages=total,
            blockedPercent=blocked_pct,
            flaggedPercent=flagged_pct,
            reviewedCount=0,
        ),
        timeline=[
            TimelinePoint(date="Mon", total=0, blocked=0, flagged=0, avgToxicity=0, spamVolume=0),
            TimelinePoint(date="Tue", total=0, blocked=0, flagged=0, avgToxicity=0, spamVolume=0),
            TimelinePoint(date="Wed", total=0, blocked=0, flagged=0, avgToxicity=0, spamVolume=0),
            TimelinePoint(date="Thu", total=0, blocked=0, flagged=0, avgToxicity=0, spamVolume=0),
            TimelinePoint(date="Fri", total=0, blocked=0, flagged=0, avgToxicity=0, spamVolume=0),
        ],
        performance=[
            PerformanceMetric(metric="True Positives", value="0"),
            PerformanceMetric(metric="False Positives", value="0"),
            PerformanceMetric(metric="True Negatives", value="0"),
            PerformanceMetric(metric="False Negatives", value="0"),
            PerformanceMetric(metric="Precision", value="N/A"),
            PerformanceMetric(metric="Recall", value="N/A"),
        ],
    )
