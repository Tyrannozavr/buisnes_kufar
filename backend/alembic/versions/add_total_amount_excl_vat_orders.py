"""add total_amount_excl_vat to orders

Revision ID: add_tot_excl_vat
Revises: add_total_amt_word
Create Date: 2026-03-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_tot_excl_vat"
down_revision: Union[str, None] = "add_total_amt_word"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"orders",
		sa.Column("total_amount_excl_vat", sa.Float(), nullable=False, server_default=sa.text("0")),
	)
	op.execute(
		"""
		UPDATE orders SET total_amount_excl_vat = CASE
			WHEN amount_with_vat_rate THEN total_amount - COALESCE(amount_vat_rate, 0)
			ELSE total_amount
		END
		"""
	)
	op.alter_column("orders", "total_amount_excl_vat", server_default=None)


def downgrade() -> None:
	op.drop_column("orders", "total_amount_excl_vat")
