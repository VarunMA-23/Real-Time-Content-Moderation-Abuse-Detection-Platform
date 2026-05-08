from typing import Any, Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api import deps
from app.services.auth import authenticate_user, build_login_response, build_oauth_token_response
from app.schemas.token import Token, LoginResponse
from app.schemas.user import User as UserSchema
from pydantic import BaseModel, EmailStr

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=LoginResponse)
def login(
    db: deps.SessionDep, 
    login_data: LoginRequest
) -> Any:
    """
    Standard login for the frontend contract.
    """
    user = authenticate_user(db, login_data.email, login_data.password)
    return build_login_response(user)

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: deps.SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    OAuth2 compatible token login, retrieve an access token for future requests
    """
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
        invalid_credentials_status=status.HTTP_400_BAD_REQUEST,
    )
    return build_oauth_token_response(user)

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: deps.CurrentUser,
) -> Any:
    """
    Get current user.
    """
    return current_user
