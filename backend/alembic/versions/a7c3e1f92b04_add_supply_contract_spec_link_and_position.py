"""add supply contract spec link and position

Revision ID: a7c3e1f92b04
Revises: d5802d7ceb54
Create Date: 2026-06-01 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7c3e1f92b04"
down_revision: Union[str, None] = "d5802d7ceb54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	op.add_column(
		"specification_item",
		sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
	)
	op.alter_column("specification_item", "position", server_default=None)

	op.add_column(
		"orders",
		sa.Column(
			"supply_spec_id",
			sa.Integer(),
			sa.ForeignKey("supply_contract_specification.id", ondelete="SET NULL"),
			nullable=True,
		),
	)
	op.create_index("ix_orders_supply_spec_id", "orders", ["supply_spec_id"])

	op.create_unique_constraint(
		"uq_supply_contract_seller_buyer_number",
		"supply_contract",
		["seller_company_id", "buyer_company_id", "number"],
	)

	op.drop_constraint("uq_supply_contracts_spec_number", "supply_contract_specification", type_="unique")
	op.create_unique_constraint(
		"uq_supply_contract_spec_number",
		"supply_contract_specification",
		["supply_contract_id", "spec_number"],
	)


def downgrade() -> None:
	"""Downgrade schema."""
	op.drop_constraint("uq_supply_contract_spec_number", "supply_contract_specification", type_="unique")
	op.create_unique_constraint(
		"uq_supply_contracts_spec_number",
		"supply_contract_specification",
		["supply_contract_id", "spec_number"],
	)

	op.drop_constraint("uq_supply_contract_seller_buyer_number", "supply_contract", type_="unique")

	op.drop_index("ix_orders_supply_spec_id", table_name="orders")
	op.drop_column("orders", "supply_spec_id")

	op.drop_column("specification_item", "position")
