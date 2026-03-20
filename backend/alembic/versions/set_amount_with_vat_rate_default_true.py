"""set amount_with_vat_rate default true

Revision ID: amount_with_vat_default_true
Revises: bill_reason_field
Create Date: 2026-03-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "amount_with_vat_default_true"
down_revision: Union[str, None] = "bill_reason_field"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.alter_column(
		"orders",
		"amount_with_vat_rate",
		existing_type=sa.Boolean(),
		server_default=sa.text("true"),
		existing_nullable=False,
	)


def downgrade() -> None:
	op.alter_column(
		"orders",
		"amount_with_vat_rate",
		existing_type=sa.Boolean(),
		server_default=sa.text("false"),
		existing_nullable=False,
	)
