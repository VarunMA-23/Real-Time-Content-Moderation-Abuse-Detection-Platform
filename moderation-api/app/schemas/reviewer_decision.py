from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel


class DecisionRequest(BaseModel):
    messageId: str
    action: str
    moderatorId: Optional[str] = None


class DecisionResponse(BaseModel):
    success: bool
