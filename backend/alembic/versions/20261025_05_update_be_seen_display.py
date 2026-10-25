"""Update the fixed Be Seen tag display text.

Revision ID: 20261025_05
Revises: 20261025_04
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa

revision = "20261025_05"
down_revision = "20261025_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            UPDATE products
            SET description = :description,
                configuration_options = CAST(:options AS jsonb)
            WHERE slug = 'small-be-seen-tag'
        """).bindparams(
            description="Fixed Be Seen tag displaying Be \u0633.",
            options='{"fixed_design":"be-seen","display_text":"Be \\u0633"}',
        )
    )


def downgrade() -> None:
    pass
