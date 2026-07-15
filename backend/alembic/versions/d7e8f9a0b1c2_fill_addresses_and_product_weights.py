"""company fill addresses + product net/gross weight (ТЗ_15 §7)

Revision ID: d7e8f9a0b1c2
Revises: c6d7e8f9a0b1
Create Date: 2026-07-15

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "d7e8f9a0b1c2"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None

fill_address_kind = sa.Enum("loading", "receiving", name="filladdresskind")


def upgrade() -> None:
	fill_address_kind.create(op.get_bind(), checkfirst=True)
	op.create_table(
		"company_fill_addresses",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("company_id", sa.Integer(), nullable=False),
		sa.Column("kind", fill_address_kind, nullable=False),
		sa.Column("address", sa.String(length=500), nullable=False),
		sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
		sa.Column("updated_at", sa.DateTime(), nullable=True),
		sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index("ix_company_fill_addresses_company_id", "company_fill_addresses", ["company_id"])
	op.create_index("ix_company_fill_addresses_kind", "company_fill_addresses", ["kind"])

	op.add_column("products", sa.Column("net_weight", sa.Float(), nullable=True))
	op.add_column("products", sa.Column("gross_weight", sa.Float(), nullable=True))


def downgrade() -> None:
	op.drop_column("products", "gross_weight")
	op.drop_column("products", "net_weight")
	op.drop_index("ix_company_fill_addresses_kind", table_name="company_fill_addresses")
	op.drop_index("ix_company_fill_addresses_company_id", table_name="company_fill_addresses")
	op.drop_table("company_fill_addresses")
	fill_address_kind.drop(op.get_bind(), checkfirst=True)
