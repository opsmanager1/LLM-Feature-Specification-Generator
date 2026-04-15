"""add feature spec runs

Revision ID: b3d1f4a90e2c
Revises: a1f9c7de42b3
Create Date: 2026-04-15 13:05:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "b3d1f4a90e2c"
down_revision = "a1f9c7de42b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feature_spec_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("feature_idea", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("response_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feature_spec_runs_user_id"),
        "feature_spec_runs",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_spec_runs_status"),
        "feature_spec_runs",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_spec_runs_created_at"),
        "feature_spec_runs",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_feature_spec_runs_created_at"), table_name="feature_spec_runs")
    op.drop_index(op.f("ix_feature_spec_runs_status"), table_name="feature_spec_runs")
    op.drop_index(op.f("ix_feature_spec_runs_user_id"), table_name="feature_spec_runs")
    op.drop_table("feature_spec_runs")
