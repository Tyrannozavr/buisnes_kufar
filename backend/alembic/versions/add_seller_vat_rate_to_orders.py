"""add seller_vat_rate to orders

Revision ID: seller_vat_rate_deal
Revises: amount_with_vat_default_true
Create Date: 2026-03-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "seller_vat_rate_deal"
down_revision: Union[str, None] = "amount_with_vat_default_true"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column("seller_vat_rate", sa.Integer(), nullable=True)
	)


def downgrade() -> None:
	op.drop_column("orders", "seller_vat_rate")
