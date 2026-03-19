"""add bill_reason to orders

Revision ID: bill_reason_field
Revises: merge_bill_heads
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bill_reason_field"
down_revision: Union[str, None] = "merge_bill_heads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column("bill_reason", sa.Text(), nullable=False, server_default="")
	)


def downgrade() -> None:
	op.drop_column("orders", "bill_reason")
