"""add supply contract tables

Revision ID: d5802d7ceb54
Revises: 2e9c77d64f91
Create Date: 2026-05-12 07:34:37.798624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5802d7ceb54'
down_revision: Union[str, None] = '2e9c77d64f91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	op.drop_table("specification_item")
	op.drop_table("supply_contract_specification")
	op.drop_table("supply_contract")

	op.drop_column("orders", "supply_contract_officials")

	op.create_table(
		"supply_contract",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column("number", sa.String(length=10), nullable=False),
		sa.Column("date", sa.DateTime(), nullable=False),
		sa.Column("officials_json", sa.JSON(), nullable=True),
		sa.Column("terms_text", sa.Text(), nullable=True),
		sa.Column("supplier_details_check", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("buyer_details_check", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("cover_letter_check", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("buyer_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
		sa.Column("seller_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
	)

	op.create_index("ix_supply_contract_buyer_company_id", "supply_contract", ["buyer_company_id"])
	op.create_index("ix_supply_contract_seller_company_id", "supply_contract", ["seller_company_id"])

	op.create_table(
		"supply_contract_specification",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column(
			"supply_contract_id",
			sa.Integer(),
			sa.ForeignKey("supply_contract.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("spec_number", sa.String(length=10), nullable=False),
		sa.Column("spec_date", sa.DateTime(), nullable=False),
		sa.Column("spec_text", sa.Text(), nullable=True),
		sa.UniqueConstraint("supply_contract_id", "spec_number", name="uq_supply_contracts_spec_number"),
	)
	op.create_index(
		"ix_supply_contract_specification_supply_contract_id",
		"supply_contract_specification",
		["supply_contract_id"],
	)

	op.create_table(
		"specification_item",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column(
			"specification_id",
			sa.Integer(),
			sa.ForeignKey("supply_contract_specification.id", ondelete="CASCADE"),
			nullable=False,
		),
		sa.Column("name", sa.String(length=255), nullable=False),
		sa.Column("article", sa.String(length=16), nullable=True),
		sa.Column("quantity", sa.Integer(), nullable=False),
		sa.Column("units", sa.String(length=32), nullable=False),
		sa.Column("price", sa.Float(), nullable=False),
		sa.Column("amount", sa.Float(), nullable=False),
	)
	op.create_index("ix_specification_item_specification_id", "specification_item", ["specification_id"])

	op.add_column(
		"orders",
		sa.Column(
			"supply_contract_id",
			sa.Integer(),
			sa.ForeignKey("supply_contract.id", ondelete="SET NULL"),
			nullable=True,
		),
	)
	op.create_index("ix_orders_supply_contract_id", "orders", ["supply_contract_id"])


def downgrade() -> None:
	"""Downgrade schema."""
	op.drop_index("ix_orders_supply_contract_id", table_name="orders")
	op.drop_column("orders", "supply_contract_id")

	op.drop_index("ix_specification_item_specification_id", table_name="specification_item")
	op.drop_table("specification_item")

	op.drop_index("ix_supply_contract_specification_supply_contract_id", table_name="supply_contract_specification")
	op.drop_table("supply_contract_specification")

	op.drop_index("ix_supply_contract_seller_company_id", table_name="supply_contract")
	op.drop_index("ix_supply_contract_buyer_company_id", table_name="supply_contract")
	op.drop_table("supply_contract")

	op.add_column("orders", sa.Column("supply_contract_officials", sa.JSON(), nullable=True))
