"""Create and seed the product catalogue.

Revision ID: 20261025_01
Revises:
Create Date: 2026-10-25
"""

from typing import Any

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20261025_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("configuration_options", sa.JSON(), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_slug", "products", ["slug"])

    products = sa.table(
        "products",
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("category", sa.String),
        sa.column("configuration_options", sa.JSON),
    )
    seed_products: list[dict[str, Any]] = [
        {
            "slug": "personalized-arabic-htv-stickers",
            "name": "Personalized Arabic HTV Stickers",
            "description": "Custom heat transfer vinyl lettering for apparel and accessories.",
            "category": "HTV Stickers",
            "configuration_options": {
                "fonts": ["Amiri", "Cairo", "Tajawal"],
                "widths_cm": [10, 15, 20],
                "colours": ["#EFFF00", "#FF6600", "#C0C0C0", "#1A1A1A"],
            },
        },
        {
            "slug": "high-visibility-tags",
            "name": "High-Visibility Tags",
            "description": "High-visibility Arabic tags for clear identification.",
            "category": "High-Visibility Tags",
            "configuration_options": {
                "shapes": ["diamond", "rectangle"],
                "fixed_designs": [{"name": "B-Series", "arabic_text": "ب س"}],
            },
        },
        {
            "slug": "be-seen-sweater",
            "name": "Be Seen Sweater",
            "description": "Black sweater with personalized Arabic text in a chosen typeface.",
            "category": "Apparel",
            "configuration_options": {
                "colour": "black",
                "personalized_text": True,
                "fonts": ["Amiri", "Cairo", "Tajawal"],
            },
        },
    ]
    statement = postgresql.insert(products).values(seed_products)
    statement = statement.on_conflict_do_nothing(index_elements=["slug"])
    op.get_bind().execute(statement)


def downgrade() -> None:
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_table("products")
