from typing import Any
from fastapi import APIRouter

from app.api import deps
from app.repositories.policy_configs import PolicyConfigsRepository
from app.schemas.policy_config import PolicyResponse
from app.services.moderation import DEFAULT_POLICY_REGION

router = APIRouter()


@router.get("/policies", response_model=PolicyResponse)
def get_policies(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> Any:
    repo = PolicyConfigsRepository(db)
    rules = repo.get_current_policy(current_user.id, DEFAULT_POLICY_REGION)
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
        region=DEFAULT_POLICY_REGION,
        rules=body.model_dump(),
        updated_by=current_user.id,
    )
    db.commit()
    return body
