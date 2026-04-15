"""enforce single prompt template row

Revision ID: c8a4e9d2f6b1
Revises: b3d1f4a90e2c
Create Date: 2026-04-15 13:45:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "c8a4e9d2f6b1"
down_revision = "b3d1f4a90e2c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    row_count = conn.execute(sa.text("SELECT COUNT(*) FROM prompt_templates")).scalar_one()
    if row_count > 1:
        raise RuntimeError(
            "Cannot enforce single-row constraint: prompt_templates has more than one row"
        )

    if row_count == 1:
        conn.execute(sa.text("UPDATE prompt_templates SET id = 1 WHERE id <> 1"))

    op.create_check_constraint(
        "ck_prompt_templates_single_row",
        "prompt_templates",
        "id = 1",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_prompt_templates_single_row",
        "prompt_templates",
        type_="check",
    )
