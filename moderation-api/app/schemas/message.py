from typing import Optional, Any, Dict, List
import uuid
from datetime import datetime
from pydantic import BaseModel


class ModerateRequest(BaseModel):
    text: str


class ModerateResponse(BaseModel):
    messageId: str
    decision: str
    scores: Dict[str, float]


class JobResponse(BaseModel):
    status: str
    llmExplanation: Optional[str] = None
    policyViolation: Optional[str] = None


class QueueItemResponse(BaseModel):
    id: str
    text: str
    userId: str
    timestamp: Optional[datetime] = None
    decision: str
    scores: Dict[str, float]
    llmExplanation: Optional[str] = None
    policyViolation: Optional[str] = None
    history: List[Dict[str, Any]] = []


class QueueResponse(BaseModel):
    queue: List[QueueItemResponse]
