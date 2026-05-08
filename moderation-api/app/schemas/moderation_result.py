from typing import Optional, Any, Dict
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ModerationResultBase(BaseModel):
    message_id: uuid.UUID
    stage: str
    risk_score: float
    labels: Dict[str, Any]
    decision: str
    model_version: str
    latency_ms: Optional[int] = None


class ModerationResultCreate(ModerationResultBase):
    pass


class ModerationResultResponse(ModerationResultBase):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
