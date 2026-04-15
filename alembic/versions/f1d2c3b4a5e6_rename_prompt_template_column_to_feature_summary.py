"""rename prompt template column to feature summary

Revision ID: f1d2c3b4a5e6
Revises: c8a4e9d2f6b1
Create Date: 2026-04-15 16:30:00.000000
"""

from alembic import op

revision = "f1d2c3b4a5e6"
down_revision = "c8a4e9d2f6b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "prompt_templates",
        "feature_to_user_stories",
        new_column_name="feature_to_feature_summary",
    )


def downgrade() -> None:
    op.alter_column(
        "prompt_templates",
        "feature_to_feature_summary",
        new_column_name="feature_to_user_stories",
    )
