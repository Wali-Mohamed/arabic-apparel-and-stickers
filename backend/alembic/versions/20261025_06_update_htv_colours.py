"""Seed the twenty HTV colour options.

Revision ID: 20261025_06
Revises: 20261025_05
Create Date: 2026-10-25
"""

import json

from alembic import op
import sqlalchemy as sa

revision = "20261025_06"
down_revision = "20261025_05"
branch_labels = None
depends_on = None

COLOURS = ["#000000", "#FFFFFF", "#FFEA00", "#37C5D3", "#E52B24", "#3AAF2A", "#EB78B8", "#2F4A92", "#5A3AA5", "#4B2117", "#167D98", "#B9999F", "#F18A00", "#BF1831", "#258FC6", "#123D2D", "#078652", "#D8BA39", "#C8CDD0", "#FF6413"]


def upgrade() -> None:
    op.execute(
        sa.text("""
            UPDATE products SET configuration_options = jsonb_set(configuration_options, '{colours}', CAST(:colours AS jsonb))
            WHERE slug = 'personalized-arabic-htv-sticker'
        """).bindparams(colours=json.dumps(COLOURS))
    )


def downgrade() -> None:
    pass
