"""add delivery_terms to orders

Revision ID: add_delivery_terms_orders
Revises: add_contract_terms_orders
Create Date: 2026-03-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_delivery_terms_orders"
down_revision: Union[str, None] = "add_contract_terms_orders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column("delivery_terms", sa.Text(), nullable=True),
	)


def downgrade() -> None:
	op.drop_column("orders", "delivery_terms")
