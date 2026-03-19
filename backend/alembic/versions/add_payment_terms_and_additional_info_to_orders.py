"""add payment_terms and additional_info to orders

Revision ID: bill_client_fields
Revises: amount_with_vat
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bill_client_fields"
down_revision: Union[str, None] = "amount_with_vat"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column("payment_terms", sa.Text(), nullable=True)
	)
	op.add_column(
		"orders",
		sa.Column("additional_info", sa.Text(), nullable=True)
	)


def downgrade() -> None:
	op.drop_column("orders", "additional_info")
	op.drop_column("orders", "payment_terms")
