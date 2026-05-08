"""PolicyConfig model for storing customer and region-specific moderation policies."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class PolicyConfig(Base):
    """
    Stores per-customer, per-region policy configuration.

    Uses append-only versioning strategy: each update creates a new row
    with an incremented version number, preserving history for audit.
    """

    __tablename__ = "policy_configs"

    # Unique constraint on (customer_id, region, version) for versioned approach
    __table_args__ = (
        UniqueConstraint("customer_id", "region", "version", name="uq_policy_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    rules: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<PolicyConfig(id={self.id}, "
            f"customer_id={self.customer_id}, "
            f"region={self.region}, "
            f"version={self.version})>"
        )
