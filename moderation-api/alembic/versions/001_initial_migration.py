"""Initial migration - create all tables and enums for ShieldAI moderation system.

Revision ID: 001_initial_migration
Revises:
Create Date: 2026-05-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_json
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_migration"
down_revision = None
branch_labels = None
depends_on = None


# Enum types to create
ENUMS = [
    ("content_type", ["text", "image", "voice"]),
    ("message_status", ["allowed", "flagged", "blocked", "pending_review", "escalated"]),
    ("moderation_stage", ["fast_model", "llm", "image"]),
    ("moderation_decision", ["allow", "warn", "block", "hold_for_review"]),
    ("reviewer_decision", ["confirm", "override", "escalate"]),
    ("reviewer_action", ["approve", "reject", "ban", "escalate"]),
    ("ingestion_channel", ["api", "webhook", "user_upload", "batch_import"]),
]


def upgrade():
    # Create enum types
    for enum_name, enum_values in ENUMS:
        postgresql.ENUM(*enum_values, name=enum_name).create(op.get_bind())

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_type", sa.Enum("text", "image", "voice", name="content_type"), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.Enum("allowed", "flagged", "blocked", "pending_review", "escalated", name="message_status"), nullable=False, server_default="allowed"),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("ingestion_channel", sa.Enum("api", "webhook", "user_upload", "batch_import", name="ingestion_channel"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_customer_id", "messages", ["customer_id"], unique=False)
    op.create_index("ix_messages_user_id", "messages", ["user_id"], unique=False)
    op.create_index("ix_messages_status", "messages", ["status"], unique=False)
    op.create_index("ix_messages_created_at", "messages", ["created_at"], unique=False)

    # Create moderation_results table
    op.create_table(
        "moderation_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("stage", sa.Enum("fast_model", "llm", "image", name="moderation_stage"), nullable=False),
        sa.Column("risk_score", sa.Double(), nullable=False),
        sa.Column("labels", sa_json.JSONB(), nullable=False, server_default="{}"),
        sa.Column("decision", sa.Enum("allow", "warn", "block", "hold_for_review", name="moderation_decision"), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_moderation_results_message_id", "moderation_results", ["message_id"], unique=False)
    op.create_index("ix_moderation_results_stage", "moderation_results", ["stage"], unique=False)
    op.create_index("ix_moderation_results_decision", "moderation_results", ["decision"], unique=False)

    # Create reviewer_decisions table
    op.create_table(
        "reviewer_decisions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("reviewer_id", sa.UUID(), nullable=False),
        sa.Column("decision", sa.Enum("confirm", "override", "escalate", name="reviewer_decision"), nullable=False),
        sa.Column("action", sa.Enum("approve", "reject", "ban", "escalate", name="reviewer_action"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviewer_decisions_message_id", "reviewer_decisions", ["message_id"], unique=False)
    op.create_index("ix_reviewer_decisions_reviewer_id", "reviewer_decisions", ["reviewer_id"], unique=False)

    # Create policy_configs table
    op.create_table(
        "policy_configs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("rules", sa_json.JSONB(), nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id", "region", "version", name="uq_policy_version"),
    )
    op.create_index("ix_policy_configs_customer_id", "policy_configs", ["customer_id"], unique=False)
    op.create_index("ix_policy_configs_region", "policy_configs", ["region"], unique=False)
    op.create_index("ix_policy_configs_updated_at", "policy_configs", ["updated_at"], unique=False)

    # Create composite indexes for common query patterns
    op.create_index("ix_messages_customer_created", "messages", ["customer_id", "created_at"], unique=False)
    op.create_index("ix_moderation_results_msg_stage", "moderation_results", ["message_id", "stage"], unique=False)
    op.create_index("ix_reviewer_decisions_msg_reviewer", "reviewer_decisions", ["message_id", "reviewer_id"], unique=False)


def downgrade():
    # Drop tables (in reverse dependency order)
    op.drop_index("ix_reviewer_decisions_msg_reviewer", table_name="reviewer_decisions")
    op.drop_index("ix_moderation_results_msg_stage", table_name="moderation_results")
    op.drop_index("ix_messages_customer_created", table_name="messages")
    op.drop_index("ix_policy_configs_updated_at", table_name="policy_configs")
    op.drop_index("ix_policy_configs_region", table_name="policy_configs")
    op.drop_index("ix_policy_configs_customer_id", table_name="policy_configs")
    op.drop_table("policy_configs")
    op.drop_index("ix_reviewer_decisions_reviewer_id", table_name="reviewer_decisions")
    op.drop_index("ix_reviewer_decisions_message_id", table_name="reviewer_decisions")
    op.drop_table("reviewer_decisions")
    op.drop_index("ix_moderation_results_decision", table_name="moderation_results")
    op.drop_index("ix_moderation_results_stage", table_name="moderation_results")
    op.drop_index("ix_moderation_results_message_id", table_name="moderation_results")
    op.drop_table("moderation_results")
    op.drop_index("ix_messages_created_at", table_name="messages")
    op.drop_index("ix_messages_status", table_name="messages")
    op.drop_index("ix_messages_user_id", table_name="messages")
    op.drop_index("ix_messages_customer_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # Drop enum types (in reverse creation order)
    op.execute("DROP TYPE IF EXISTS ingestion_channel")
    op.execute("DROP TYPE IF EXISTS reviewer_action")
    op.execute("DROP TYPE IF EXISTS reviewer_decision")
    op.execute("DROP TYPE IF EXISTS moderation_decision")
    op.execute("DROP TYPE IF EXISTS moderation_stage")
    op.execute("DROP TYPE IF EXISTS message_status")
    op.execute("DROP TYPE IF EXISTS content_type")
