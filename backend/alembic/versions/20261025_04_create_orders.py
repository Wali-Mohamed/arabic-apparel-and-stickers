"""Create admin order requests.

Revision ID: 20261025_04
Revises: 20261025_03
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa

revision = "20261025_04"
down_revision = "20261025_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("customer_name", sa.String(length=200), nullable=False),
        sa.Column("customer_contact", sa.String(length=320), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price_pence", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("orders")
