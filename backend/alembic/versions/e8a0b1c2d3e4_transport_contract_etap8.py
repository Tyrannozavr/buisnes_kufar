"""transport contract JSON on orders (ТЗ_15 §8.5)

Revision ID: e8a0b1c2d3e4
Revises: d7e8f9a0b1c2
Create Date: 2026-07-15

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "e8a0b1c2d3e4"
down_revision = "d7e8f9a0b1c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.add_column("orders", sa.Column("transport_contract", sa.JSON(), nullable=True))


def downgrade() -> None:
	op.drop_column("orders", "transport_contract")
