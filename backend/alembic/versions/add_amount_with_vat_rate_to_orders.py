"""add amount_with_vat_rate to orders

Revision ID: amount_with_vat
Revises: bill_officials
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "amount_with_vat"
down_revision: Union[str, None] = "bill_officials"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column("amount_with_vat_rate", sa.Boolean(), nullable=False, server_default="false")
	)


def downgrade() -> None:
	op.drop_column("orders", "amount_with_vat_rate")
