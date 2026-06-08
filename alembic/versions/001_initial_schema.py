"""Initial schema — creates all tables

Revision ID: 001
Revises:
Create Date: 2026-06-08
"""
from typing import Sequence, Union
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            name    VARCHAR(100) NOT NULL,
            email   VARCHAR(255) NOT NULL UNIQUE,
            phone   VARCHAR(20)  NOT NULL UNIQUE
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            name       VARCHAR(255) NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS product_variants (
            variant_id SERIAL PRIMARY KEY,
            product_id INTEGER       NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
            color      VARCHAR(50),
            size       VARCHAR(50),
            price      NUMERIC(10,2) NOT NULL CHECK (price > 0),
            stock      INTEGER       NOT NULL DEFAULT 0 CHECK (stock >= 0)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            cart_id SERIAL PRIMARY KEY,
            user_id INTEGER     NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            status  VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'checked_out'))
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            item_id    SERIAL  PRIMARY KEY,
            cart_id    INTEGER NOT NULL REFERENCES carts(cart_id)               ON DELETE CASCADE,
            variant_id INTEGER NOT NULL REFERENCES product_variants(variant_id) ON DELETE CASCADE,
            quantity   INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
            UNIQUE (cart_id, variant_id)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS cart_items")
    op.execute("DROP TABLE IF EXISTS carts")
    op.execute("DROP TABLE IF EXISTS product_variants")
    op.execute("DROP TABLE IF EXISTS products")
    op.execute("DROP TABLE IF EXISTS users")
