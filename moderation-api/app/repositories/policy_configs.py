"""PolicyConfigs repository for data access abstraction."""
import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.policy_config import PolicyConfig


class PolicyConfigsRepository:
    """Repository for PolicyConfig entity operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, customer_id: uuid.UUID, region: str, rules: Dict[str, Any],
               updated_by: Optional[uuid.UUID] = None) -> PolicyConfig:
        """Create a new policy config version."""
        # Get the current max version for this customer/region
        current_max = (
            self.db.query(PolicyConfig.version)
            .filter(PolicyConfig.customer_id == customer_id, PolicyConfig.region == region)
            .order_by(desc(PolicyConfig.version))
            .limit(1)
            .scalar()
        )

        new_version = (current_max or 0) + 1

        config = PolicyConfig(
            customer_id=customer_id,
            region=region,
            rules=rules,
            version=new_version,
            updated_by=updated_by,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def find_by_id(self, config_id: uuid.UUID) -> Optional[PolicyConfig]:
        """Retrieve a policy config by ID."""
        return self.db.query(PolicyConfig).filter(PolicyConfig.id == config_id).first()

    def find_latest_by_customer_and_region(self, customer_id: uuid.UUID, region: str) -> Optional[PolicyConfig]:
        """Get the latest active policy config for a customer and region."""
        stmt = (
            select(PolicyConfig)
            .where(
                PolicyConfig.customer_id == customer_id,
                PolicyConfig.region == region
            )
            .order_by(desc(PolicyConfig.version))
            .limit(1)
        )
        return self.db.scalar(stmt)

    def find_all_versions(self, customer_id: uuid.UUID, region: str) -> List[PolicyConfig]:
        """Get all policy versions for a customer and region (for audit)."""
        stmt = (
            select(PolicyConfig)
            .where(
                PolicyConfig.customer_id == customer_id,
                PolicyConfig.region == region
            )
            .order_by(desc(PolicyConfig.version))
        )
        return list(self.db.scalars(stmt).all())

    def get_current_policy(self, customer_id: uuid.UUID, region: str) -> Dict[str, Any]:
        """Get current policy rules or return defaults if none exist."""
        config = self.find_latest_by_customer_and_region(customer_id, region)
        if config:
            return config.rules

        # Return default policy rules
        return {
            "toxicityThreshold": 0.7,
            "spamThreshold": 0.6,
            "selfHarmThreshold": 0.5,
            "hateSpeechThreshold": 0.7,
            "autoBlock": False,
            "llmReview": True,
        }

    def update_policy(self, customer_id: uuid.UUID, region: str, rules: Dict[str, Any],
                      updated_by: Optional[uuid.UUID] = None) -> PolicyConfig:
        """Update policy with a new version."""
        # First get the current latest to copy rules from if needed
        current = self.find_latest_by_customer_and_region(customer_id, region)

        # Create new version
        return self.create(customer_id=customer_id, region=region, rules=rules, updated_by=updated_by)

    def find_by_customer(self, customer_id: uuid.UUID) -> List[PolicyConfig]:
        """Get all policy configs for a customer (across all regions)."""
        stmt = (
            select(PolicyConfig)
            .where(PolicyConfig.customer_id == customer_id)
            .order_by(desc(PolicyConfig.updated_at))
        )
        return list(self.db.scalars(stmt).all())

    def get_customer_region_policies(self, customer_id: uuid.UUID) -> Dict[str, Dict[str, Any]]:
        """Get current policy for each region a customer has configured."""
        stmt = (
            select(PolicyConfig.region, PolicyConfig.rules)
            .where(PolicyConfig.customer_id == customer_id)
            .distinct(PolicyConfig.region)
        )

        # Get latest version for each region
        results = self.db.execute(stmt).all()
        return {region: rules for region, rules in results}
