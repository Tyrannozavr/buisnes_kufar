"""add payment_terms for bill-payment (Счет на оплату)

Revision ID: e5a2b3c4d6f7
Revises: c4f8a1b2d3e5
Create Date: 2026-06-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5a2b3c4d6f7"
down_revision: Union[str, None] = "c4f8a1b2d3e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column("orders", sa.Column("payment_terms", sa.Text(), nullable=True))


def downgrade() -> None:
	op.drop_column("orders", "payment_terms")
