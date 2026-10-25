"""Add demonstration catalogue prices in integer pence.

Revision ID: 20261025_02
Revises: 20261025_01
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa

revision = "20261025_02"
down_revision = "20261025_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_key", sa.String(length=50), nullable=False),
        sa.Column("option_value", sa.String(length=100), nullable=False),
        sa.Column("price_pence", sa.Integer(), nullable=False),
        sa.CheckConstraint("price_pence >= 0", name="ck_product_prices_price_pence_nonnegative"),
        sa.UniqueConstraint("product_id", "option_key", "option_value"),
    )

    price_rows = [
        ("personalized-arabic-htv-stickers", "width_cm", "10", 499),
        ("personalized-arabic-htv-stickers", "width_cm", "15", 699),
        ("personalized-arabic-htv-stickers", "width_cm", "20", 899),
        ("high-visibility-tags", "shape", "diamond", 599),
        ("high-visibility-tags", "shape", "rectangle", 699),
        ("high-visibility-tags", "design", "b-series", 599),
        ("be-seen-sweater", "standard", "standard", 2499),
    ]
    for slug, option_key, option_value, price_pence in price_rows:
        op.execute(
            sa.text(
                """
                INSERT INTO product_prices (product_id, option_key, option_value, price_pence)
                SELECT id, :option_key, :option_value, :price_pence
                FROM products WHERE slug = :slug
                ON CONFLICT (product_id, option_key, option_value) DO NOTHING
                """
            ).bindparams(
                slug=slug,
                option_key=option_key,
                option_value=option_value,
                price_pence=price_pence,
            )
        )


def downgrade() -> None:
    op.drop_table("product_prices")
