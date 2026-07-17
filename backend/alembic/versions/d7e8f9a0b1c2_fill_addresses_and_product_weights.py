"""company fill addresses + product net/gross weight (ТЗ_15 §7)

Revision ID: d7e8f9a0b1c2
Revises: c6d7e8f9a0b1
Create Date: 2026-07-15

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "d7e8f9a0b1c2"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None

fill_address_kind = postgresql.ENUM(
	"loading",
	"receiving",
	name="filladdresskind",
	create_type=False,
)


def upgrade() -> None:
	bind = op.get_bind()
	# create_type=False + явный CREATE избегает двойного CREATE TYPE при create_table
	op.execute(
		"""
		DO $$ BEGIN
			CREATE TYPE filladdresskind AS ENUM ('loading', 'receiving');
		EXCEPTION
			WHEN duplicate_object THEN NULL;
		END $$;
		"""
	)

	inspector = sa.inspect(bind)
	tables = set(inspector.get_table_names())
	if "company_fill_addresses" not in tables:
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
	op.execute(
		"CREATE INDEX IF NOT EXISTS ix_company_fill_addresses_company_id "
		"ON company_fill_addresses (company_id)"
	)
	op.execute(
		"CREATE INDEX IF NOT EXISTS ix_company_fill_addresses_kind "
		"ON company_fill_addresses (kind)"
	)

	product_cols = {c["name"] for c in inspector.get_columns("products")}
	if "net_weight" not in product_cols:
		op.add_column("products", sa.Column("net_weight", sa.Float(), nullable=True))
	if "gross_weight" not in product_cols:
		op.add_column("products", sa.Column("gross_weight", sa.Float(), nullable=True))


def downgrade() -> None:
	op.drop_column("products", "gross_weight")
	op.drop_column("products", "net_weight")
	op.drop_index("ix_company_fill_addresses_kind", table_name="company_fill_addresses")
	op.drop_index("ix_company_fill_addresses_company_id", table_name="company_fill_addresses")
	op.drop_table("company_fill_addresses")
	op.execute("DROP TYPE IF EXISTS filladdresskind")
