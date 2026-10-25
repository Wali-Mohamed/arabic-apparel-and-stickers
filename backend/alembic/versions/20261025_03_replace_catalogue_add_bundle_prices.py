"""Replace the demonstration catalogue and add pair prices.

Revision ID: 20261025_03
Revises: 20261025_02
Create Date: 2026-10-25
"""

import json

from alembic import op
import sqlalchemy as sa

revision = "20261025_03"
down_revision = "20261025_02"
branch_labels = None
depends_on = None


PRODUCTS = [
    ("small-be-seen-tag", "Small Be Seen tag", "Fixed Be Seen tag displaying Be س.", "Be Seen Tags", {"fixed_design": "be-seen", "display_text": "Be \u0633"}),
    ("big-be-seen-tag", "Big Be Seen tag", "Large Be Seen tag.", "Be Seen Tags", {}),
    ("personalized-arabic-rectangular-tag", "Personalized Arabic rectangular tag", "A long-name Arabic rectangular tag.", "Be Seen Tags", {"fonts": ["Amiri", "Cairo", "Tajawal"], "max_graphemes": 24}),
    ("small-arabic-letter-tag", "Small Arabic letter-only tag", "A tag for one Arabic letter, with optional diacritics.", "Be Seen Tags", {"fonts": ["Amiri", "Cairo", "Tajawal"], "letter_only": True}),
    ("personalized-arabic-htv-sticker", "Personalized Arabic HTV sticker", "Arabic HTV lettering in three inch sizes.", "HTV Stickers", {"fonts": ["Amiri", "Cairo", "Tajawal"], "sizes": ["5x5", "9x4", "12x3"], "colours": ["#000000", "#FFFFFF", "#FFEA00", "#37C5D3", "#E52B24", "#3AAF2A", "#EB78B8", "#2F4A92", "#5A3AA5", "#4B2117", "#167D98", "#B9999F", "#F18A00", "#BF1831", "#258FC6", "#123D2D", "#078652", "#D8BA39", "#C8CDD0", "#FF6413"], "max_graphemes": 24}),
    ("be-seen-boys-sweater", "Be Seen boys' sweater", "Black sweater with a personalized Arabic name.", "Apparel", {"colour": "black", "fonts": ["Amiri", "Cairo", "Tajawal"], "max_graphemes": 24}),
    ("be-seen-mens-sweater", "Be Seen men's sweater", "Black sweater with a personalized Arabic name.", "Apparel", {"colour": "black", "fonts": ["Amiri", "Cairo", "Tajawal"], "max_graphemes": 24}),
    ("be-seen-black-canvas-bag", "Be Seen black canvas bag", "Black canvas bag.", "Accessories", {"colour": "black"}),
]

PRICES = [
    ("small-be-seen-tag", "standard", "standard", 500, None),
    ("big-be-seen-tag", "standard", "standard", 1000, None),
    ("personalized-arabic-rectangular-tag", "standard", "standard", 1200, None),
    ("small-arabic-letter-tag", "standard", "standard", 500, 850),
    ("personalized-arabic-htv-sticker", "size", "5x5", 500, None),
    ("personalized-arabic-htv-sticker", "size", "9x4", 900, None),
    ("personalized-arabic-htv-sticker", "size", "12x3", 1200, None),
    ("be-seen-boys-sweater", "standard", "standard", 1500, 2500),
    ("be-seen-mens-sweater", "standard", "standard", 3000, 5000),
    ("be-seen-black-canvas-bag", "standard", "standard", 2000, None),
]


def upgrade() -> None:
    op.execute("ALTER TABLE product_prices ADD COLUMN IF NOT EXISTS pair_price_pence INTEGER")
    bind = op.get_bind()
    old_slugs = ("personalized-arabic-htv-stickers", "high-visibility-tags", "be-seen-sweater")
    bind.execute(sa.text("DELETE FROM products WHERE slug IN :slugs").bindparams(sa.bindparam("slugs", expanding=True)), {"slugs": old_slugs})

    for slug, name, description, category, options in PRODUCTS:
        bind.execute(
            sa.text("""
                INSERT INTO products (slug, name, description, category, configuration_options)
                VALUES (:slug, :name, :description, :category, CAST(:options AS jsonb))
                ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description,
                  category = EXCLUDED.category, configuration_options = EXCLUDED.configuration_options
            """),
            {"slug": slug, "name": name, "description": description, "category": category, "options": json.dumps(options)},
        )

    for slug, option_key, option_value, price_pence, pair_price_pence in PRICES:
        bind.execute(
            sa.text("""
                INSERT INTO product_prices (product_id, option_key, option_value, price_pence, pair_price_pence)
                SELECT id, :option_key, :option_value, :price_pence, :pair_price_pence FROM products WHERE slug = :slug
                ON CONFLICT (product_id, option_key, option_value) DO UPDATE SET
                  price_pence = EXCLUDED.price_pence, pair_price_pence = EXCLUDED.pair_price_pence
            """),
            {"slug": slug, "option_key": option_key, "option_value": option_value, "price_pence": price_pence, "pair_price_pence": pair_price_pence},
        )


def downgrade() -> None:
    op.drop_column("product_prices", "pair_price_pence")
