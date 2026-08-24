"""Create mandi_prices cache table.

Revision ID: 001_mandi_prices
Revises:
Create Date: 2026-08-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_mandi_prices"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mandi_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("state", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("district", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("market", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("commodity", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("variety", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("min_price", sa.Float(), nullable=True),
        sa.Column("max_price", sa.Float(), nullable=True),
        sa.Column("modal_price", sa.Float(), nullable=True),
        sa.Column("arrival_date", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_mandi_prices_state", "mandi_prices", ["state"])
    op.create_index("ix_mandi_prices_district", "mandi_prices", ["district"])
    op.create_index("ix_mandi_prices_market", "mandi_prices", ["market"])
    op.create_index("ix_mandi_prices_commodity", "mandi_prices", ["commodity"])
    op.create_index("ix_mandi_prices_updated_at", "mandi_prices", ["updated_at"])
    op.create_index(
        "ix_mandi_prices_lookup",
        "mandi_prices",
        ["commodity", "state", "district"],
    )
    op.create_unique_constraint(
        "uq_mandi_price_row",
        "mandi_prices",
        ["state", "district", "market", "commodity", "variety", "arrival_date"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_mandi_price_row", "mandi_prices", type_="unique")
    op.drop_index("ix_mandi_prices_lookup", table_name="mandi_prices")
    op.drop_index("ix_mandi_prices_updated_at", table_name="mandi_prices")
    op.drop_index("ix_mandi_prices_commodity", table_name="mandi_prices")
    op.drop_index("ix_mandi_prices_market", table_name="mandi_prices")
    op.drop_index("ix_mandi_prices_district", table_name="mandi_prices")
    op.drop_index("ix_mandi_prices_state", table_name="mandi_prices")
    op.drop_table("mandi_prices")
