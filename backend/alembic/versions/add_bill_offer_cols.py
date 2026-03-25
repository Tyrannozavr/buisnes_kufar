"""add bill offer fields to orders

Revision ID: add_bill_offer_cols
Revises: rename_bill_contract_cols
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_bill_offer_cols"
down_revision: Union[str, None] = "rename_bill_contract_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column("orders", sa.Column("payment_terms_offer", sa.Text(), nullable=True))
	op.add_column(
		"orders",
		sa.Column(
			"contract_terms_offer",
			sa.String(length=64),
			nullable=False,
			server_default="standard-delivery-supplier",
		),
	)
	op.add_column(
		"orders",
		sa.Column(
			"contract_terms_text_offer",
			sa.Text(),
			nullable=False,
			server_default="",
		),
	)
	op.add_column("orders", sa.Column("additional_info_offer", sa.Text(), nullable=True))
	op.alter_column(
		"orders",
		"contract_terms_offer",
		server_default=None,
		existing_type=sa.String(length=64),
		existing_nullable=False,
	)
	op.alter_column(
		"orders",
		"contract_terms_text_offer",
		server_default=None,
		existing_type=sa.Text(),
		existing_nullable=False,
	)


def downgrade() -> None:
	op.drop_column("orders", "additional_info_offer")
	op.drop_column("orders", "contract_terms_text_offer")
	op.drop_column("orders", "contract_terms_offer")
	op.drop_column("orders", "payment_terms_offer")
