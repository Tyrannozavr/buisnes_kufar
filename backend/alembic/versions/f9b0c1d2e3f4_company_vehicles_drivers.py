"""company vehicles and drivers (ТЗ_15 ЛК Транспорт / Водители)

Revision ID: f9b0c1d2e3f4
Revises: e8a0b1c2d3e4
Create Date: 2026-07-17

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f9b0c1d2e3f4"
down_revision = "e8a0b1c2d3e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
	bind = op.get_bind()
	inspector = sa.inspect(bind)
	tables = set(inspector.get_table_names())

	if "company_vehicles" not in tables:
		op.create_table(
			"company_vehicles",
			sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
			sa.Column("company_id", sa.Integer(), nullable=False),
			sa.Column("name", sa.String(length=200), nullable=False),
			sa.Column("plate_number", sa.String(length=32), nullable=True),
			sa.Column("vehicle_type", sa.String(length=100), nullable=True),
			sa.Column("capacity_tons", sa.Float(), nullable=True),
			sa.Column("volume_m3", sa.Float(), nullable=True),
			sa.Column("notes", sa.String(length=500), nullable=True),
			sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
			sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
			sa.Column("updated_at", sa.DateTime(), nullable=True),
			sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
			sa.PrimaryKeyConstraint("id"),
		)
	op.execute("CREATE INDEX IF NOT EXISTS ix_company_vehicles_company_id ON company_vehicles (company_id)")

	if "company_drivers" not in tables:
		op.create_table(
			"company_drivers",
			sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
			sa.Column("company_id", sa.Integer(), nullable=False),
			sa.Column("full_name", sa.String(length=200), nullable=False),
			sa.Column("phone", sa.String(length=32), nullable=True),
			sa.Column("license_number", sa.String(length=64), nullable=True),
			sa.Column("notes", sa.String(length=500), nullable=True),
			sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
			sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
			sa.Column("updated_at", sa.DateTime(), nullable=True),
			sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
			sa.PrimaryKeyConstraint("id"),
		)
	op.execute("CREATE INDEX IF NOT EXISTS ix_company_drivers_company_id ON company_drivers (company_id)")


def downgrade() -> None:
	op.drop_index("ix_company_drivers_company_id", table_name="company_drivers")
	op.drop_table("company_drivers")
	op.drop_index("ix_company_vehicles_company_id", table_name="company_vehicles")
	op.drop_table("company_vehicles")
