from typing import Optional
import uuid
from pydantic import BaseModel
from app.schemas.user import User

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class LoginResponse(BaseModel):
    user: User
    accessToken: str
    expiresIn: int
