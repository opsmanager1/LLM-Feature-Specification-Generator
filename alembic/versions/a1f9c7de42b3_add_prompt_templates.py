"""add prompt templates

Revision ID: a1f9c7de42b3
Revises: 6f4e8b8f4b11
Create Date: 2026-04-15 12:15:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "a1f9c7de42b3"
down_revision = "6f4e8b8f4b11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feature_to_user_stories", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("prompt_templates")