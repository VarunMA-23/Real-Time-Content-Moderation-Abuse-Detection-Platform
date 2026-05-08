from typing import Any
import uuid
from fastapi import APIRouter

from app.api import deps
from app.repositories.policy_configs import PolicyConfigsRepository
from app.schemas.policy_config import PolicyResponse

router = APIRouter()


@router.get("/policies", response_model=PolicyResponse)
def get_policies(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> Any:
    repo = PolicyConfigsRepository(db)
    rules = repo.get_current_policy(current_user.id, "US")
    return PolicyResponse(**rules)


@router.put("/policies", response_model=PolicyResponse)
def update_policies(
    db: deps.SessionDep,
    body: PolicyResponse,
    current_user: deps.CurrentUser,
) -> Any:
    repo = PolicyConfigsRepository(db)
    repo.update_policy(
        customer_id=current_user.id,
        region="US",
        rules=body.model_dump(),
        updated_by=current_user.id,
    )
    return body
