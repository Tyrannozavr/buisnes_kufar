"""add contract_terms and contract_terms_text to orders

Revision ID: add_contract_terms_orders
Revises: deal_amount_vat_rate
Create Date: 2026-03-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_contract_terms_orders"
down_revision: Union[str, None] = "deal_amount_vat_rate"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column(
			"contract_terms",
			sa.String(length=64),
			nullable=False,
			server_default="standard-delivery-supplier",
		),
	)
	op.add_column(
		"orders",
		sa.Column(
			"contract_terms_text",
			sa.Text(),
			nullable=False,
			server_default="",
		),
	)


def downgrade() -> None:
	op.drop_column("orders", "contract_terms_text")
	op.drop_column("orders", "contract_terms")
