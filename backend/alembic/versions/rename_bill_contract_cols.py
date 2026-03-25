"""rename bill contract-related columns on orders (_contract suffix)

Revision ID: rename_bill_contract_cols
Revises: add_delivery_terms_orders
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "rename_bill_contract_cols"
down_revision: Union[str, None] = "add_delivery_terms_orders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.alter_column(
		"orders",
		"payment_terms",
		new_column_name="payment_terms_contract",
		existing_type=sa.Text(),
		existing_nullable=True,
	)
	op.alter_column(
		"orders",
		"delivery_terms",
		new_column_name="delivery_terms_contract",
		existing_type=sa.Text(),
		existing_nullable=True,
	)
	op.alter_column(
		"orders",
		"contract_terms",
		new_column_name="contract_terms_contract",
		existing_type=sa.String(length=64),
		existing_nullable=False,
	)
	op.alter_column(
		"orders",
		"contract_terms_text",
		new_column_name="contract_terms_text_contract",
		existing_type=sa.Text(),
		existing_nullable=False,
	)


def downgrade() -> None:
	op.alter_column(
		"orders",
		"payment_terms_contract",
		new_column_name="payment_terms",
		existing_type=sa.Text(),
		existing_nullable=True,
	)
	op.alter_column(
		"orders",
		"delivery_terms_contract",
		new_column_name="delivery_terms",
		existing_type=sa.Text(),
		existing_nullable=True,
	)
	op.alter_column(
		"orders",
		"contract_terms_contract",
		new_column_name="contract_terms",
		existing_type=sa.String(length=64),
		existing_nullable=False,
	)
	op.alter_column(
		"orders",
		"contract_terms_text_contract",
		new_column_name="contract_terms_text",
		existing_type=sa.Text(),
		existing_nullable=False,
	)
