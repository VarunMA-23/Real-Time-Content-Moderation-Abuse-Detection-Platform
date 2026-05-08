from typing import Optional, Any, Dict
import uuid
from datetime import datetime
from pydantic import BaseModel


class PolicyResponse(BaseModel):
    toxicityThreshold: float = 0.7
    spamThreshold: float = 0.6
    selfHarmThreshold: float = 0.5
    hateSpeechThreshold: float = 0.7
    autoBlock: bool = False
    llmReview: bool = True
