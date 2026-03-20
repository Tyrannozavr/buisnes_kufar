"""add amount_vat_rate to orders

Revision ID: deal_amount_vat_rate
Revises: seller_vat_rate_deal
Create Date: 2026-03-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "deal_amount_vat_rate"
down_revision: Union[str, None] = "seller_vat_rate_deal"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column("amount_vat_rate", sa.Float(), nullable=False, server_default="0")
	)


def downgrade() -> None:
	op.drop_column("orders", "amount_vat_rate")
