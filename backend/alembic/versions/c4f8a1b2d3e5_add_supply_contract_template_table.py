"""add supply contract template table

Revision ID: c4f8a1b2d3e5
Revises: a7c3e1f92b04
Create Date: 2026-06-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4f8a1b2d3e5"
down_revision: Union[str, None] = "a7c3e1f92b04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

supply_contract_template_type = sa.Enum(
	"supply_contract",
	"specification",
	name="supplycontracttemplatetype",
)


def upgrade() -> None:
	supply_contract_template_type.create(op.get_bind(), checkfirst=True)
	op.create_table(
		"supply_contract_template",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("company_id", sa.Integer(), nullable=False),
		sa.Column("type", supply_contract_template_type, nullable=False),
		sa.Column("name", sa.String(length=128), nullable=False),
		sa.Column("content_html", sa.Text(), nullable=False, server_default=""),
		sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("created_at", sa.DateTime(), nullable=True),
		sa.Column("updated_at", sa.DateTime(), nullable=True),
		sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
		sa.PrimaryKeyConstraint("id"),
		sa.UniqueConstraint(
			"company_id",
			"type",
			"name",
			name="uq_supply_contract_template_company_type_name",
		),
	)
	op.create_index(
		"ix_supply_contract_template_company_id",
		"supply_contract_template",
		["company_id"],
	)
	op.create_index(
		"ix_supply_contract_template_type",
		"supply_contract_template",
		["type"],
	)
	op.add_column(
		"orders",
		sa.Column("supply_contract_template_id", sa.Integer(), nullable=True),
	)
	op.add_column(
		"orders",
		sa.Column("supply_specification_template_id", sa.Integer(), nullable=True),
	)
	op.create_foreign_key(
		"fk_orders_supply_contract_template_id",
		"orders",
		"supply_contract_template",
		["supply_contract_template_id"],
		["id"],
		ondelete="SET NULL",
	)
	op.create_foreign_key(
		"fk_orders_supply_specification_template_id",
		"orders",
		"supply_contract_template",
		["supply_specification_template_id"],
		["id"],
		ondelete="SET NULL",
	)
	op.create_index("ix_orders_supply_contract_template_id", "orders", ["supply_contract_template_id"])
	op.create_index("ix_orders_supply_specification_template_id", "orders", ["supply_specification_template_id"])


def downgrade() -> None:
	op.drop_index("ix_orders_supply_specification_template_id", table_name="orders")
	op.drop_index("ix_orders_supply_contract_template_id", table_name="orders")
	op.drop_constraint("fk_orders_supply_specification_template_id", "orders", type_="foreignkey")
	op.drop_constraint("fk_orders_supply_contract_template_id", "orders", type_="foreignkey")
	op.drop_column("orders", "supply_specification_template_id")
	op.drop_column("orders", "supply_contract_template_id")
	op.drop_index("ix_supply_contract_template_type", table_name="supply_contract_template")
	op.drop_index("ix_supply_contract_template_company_id", table_name="supply_contract_template")
	op.drop_table("supply_contract_template")
	supply_contract_template_type.drop(op.get_bind(), checkfirst=True)
