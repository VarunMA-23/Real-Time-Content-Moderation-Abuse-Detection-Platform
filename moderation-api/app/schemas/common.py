from typing import Optional, Any, Dict, List
from pydantic import BaseModel
from datetime import datetime


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class SuccessResponse(BaseModel):
    success: bool = True


class TimelinePoint(BaseModel):
    date: str
    total: int
    blocked: int
    flagged: int
    avgToxicity: float
    spamVolume: int


class PerformanceMetric(BaseModel):
    metric: str
    value: str


class AnalyticsTotals(BaseModel):
    totalMessages: int = 0
    blockedPercent: float = 0
    flaggedPercent: float = 0
    reviewedCount: int = 0


class AnalyticsResponse(BaseModel):
    totals: AnalyticsTotals
    timeline: List[TimelinePoint]
    performance: List[PerformanceMetric]
