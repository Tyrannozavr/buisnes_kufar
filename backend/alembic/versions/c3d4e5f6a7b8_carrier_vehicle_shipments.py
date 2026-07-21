"""carrier vehicle fields and shipment transport workflow

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-22
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def _add_column_if_missing(table: str, column: sa.Column) -> None:
	columns = {item["name"] for item in sa.inspect(op.get_bind()).get_columns(table)}
	if column.name not in columns:
		op.add_column(table, column)


def _create_table_if_missing(name: str, *args, **kwargs) -> None:
	tables = set(sa.inspect(op.get_bind()).get_table_names())
	if name not in tables:
		op.create_table(name, *args, **kwargs)


def upgrade() -> None:
	_add_column_if_missing("company_vehicles", sa.Column("trailer_plate_number", sa.String(32), nullable=True))
	_add_column_if_missing("company_vehicles", sa.Column("trailer_length_m", sa.Float(), nullable=True))
	_add_column_if_missing("company_vehicles", sa.Column("trailer_width_m", sa.Float(), nullable=True))
	_add_column_if_missing("company_vehicles", sa.Column("trailer_height_m", sa.Float(), nullable=True))
	_add_column_if_missing("company_vehicles", sa.Column("load_date", sa.Date(), nullable=True))
	_add_column_if_missing("company_vehicles", sa.Column("body_type", sa.String(100), nullable=True))
	_add_column_if_missing("company_vehicles", sa.Column("loading_methods", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
	_add_column_if_missing("company_vehicles", sa.Column("adr_classes", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
	_add_column_if_missing("company_vehicles", sa.Column("from_locations", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
	_add_column_if_missing("company_vehicles", sa.Column("to_locations", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
	_add_column_if_missing("company_vehicles", sa.Column("partial_load", sa.Boolean(), nullable=False, server_default=sa.false()))
	_add_column_if_missing("company_vehicles", sa.Column("partial_load_weight_kg", sa.Float(), nullable=True))
	_add_column_if_missing("company_vehicles", sa.Column("partial_load_volume_m3", sa.Float(), nullable=True))
	_add_column_if_missing("company_drivers", sa.Column("inn", sa.String(16), nullable=True))

	_create_table_if_missing(
		"shipment_requests",
		sa.Column("id", sa.Integer(), primary_key=True),
		sa.Column("client_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
		sa.Column("carrier_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
		sa.Column("status", sa.String(16), nullable=False, server_default="passive"),
		sa.Column("is_highlighted", sa.Boolean(), nullable=False, server_default=sa.false()),
		sa.Column("search_filters", sa.JSON(), nullable=False),
		sa.Column("matched_vehicle_ids", sa.JSON(), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.Column("updated_at", sa.DateTime(), nullable=False),
		sa.Column("activated_at", sa.DateTime(), nullable=True),
		sa.Column("expires_at", sa.DateTime(), nullable=False),
	)
	op.execute("CREATE INDEX IF NOT EXISTS ix_shipment_requests_client_company_id ON shipment_requests (client_company_id)")
	op.execute("CREATE INDEX IF NOT EXISTS ix_shipment_requests_carrier_company_id ON shipment_requests (carrier_company_id)")
	op.execute("CREATE INDEX IF NOT EXISTS ix_shipment_requests_status ON shipment_requests (status)")
	op.execute("CREATE INDEX IF NOT EXISTS ix_shipment_requests_expires_at ON shipment_requests (expires_at)")

	_create_table_if_missing(
		"shipments",
		sa.Column("id", sa.Integer(), primary_key=True),
		sa.Column("number", sa.String(5), nullable=False),
		sa.Column("year", sa.Integer(), nullable=False),
		sa.Column("client_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
		sa.Column("carrier_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
		sa.Column("request_id", sa.Integer(), sa.ForeignKey("shipment_requests.id", ondelete="CASCADE"), nullable=False, unique=True),
		sa.Column("deal_id", sa.Integer(), nullable=True, unique=True),
		sa.Column("cargo_data", sa.JSON(), nullable=False),
		sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("company_vehicles.id", ondelete="SET NULL"), nullable=True),
		sa.Column("driver_id", sa.Integer(), sa.ForeignKey("company_drivers.id", ondelete="SET NULL"), nullable=True),
		sa.Column("transport_snapshot", sa.JSON(), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.Column("updated_at", sa.DateTime(), nullable=False),
	)
	op.execute("CREATE INDEX IF NOT EXISTS ix_shipments_year ON shipments (year)")
	op.execute("CREATE INDEX IF NOT EXISTS ix_shipments_client_company_id ON shipments (client_company_id)")
	op.execute("CREATE INDEX IF NOT EXISTS ix_shipments_carrier_company_id ON shipments (carrier_company_id)")

	_create_table_if_missing(
		"vehicle_favorites",
		sa.Column("id", sa.Integer(), primary_key=True),
		sa.Column("client_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
		sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("company_vehicles.id", ondelete="CASCADE"), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.UniqueConstraint("client_company_id", "vehicle_id", name="uq_vehicle_favorite_company_vehicle"),
	)
	op.execute("CREATE INDEX IF NOT EXISTS ix_vehicle_favorites_client_company_id ON vehicle_favorites (client_company_id)")
	op.execute("CREATE INDEX IF NOT EXISTS ix_vehicle_favorites_vehicle_id ON vehicle_favorites (vehicle_id)")

	_create_table_if_missing(
		"request_favorites",
		sa.Column("id", sa.Integer(), primary_key=True),
		sa.Column("carrier_company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
		sa.Column("request_id", sa.Integer(), sa.ForeignKey("shipment_requests.id", ondelete="CASCADE"), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.UniqueConstraint("carrier_company_id", "request_id", name="uq_request_favorite_company_request"),
	)
	op.execute("CREATE INDEX IF NOT EXISTS ix_request_favorites_carrier_company_id ON request_favorites (carrier_company_id)")
	op.execute("CREATE INDEX IF NOT EXISTS ix_request_favorites_request_id ON request_favorites (request_id)")


def downgrade() -> None:
	op.drop_table("request_favorites")
	op.drop_table("vehicle_favorites")
	op.drop_table("shipments")
	op.drop_table("shipment_requests")
	for name in (
		"partial_load_volume_m3", "partial_load_weight_kg", "partial_load", "to_locations",
		"from_locations", "adr_classes", "loading_methods", "body_type", "load_date",
		"trailer_height_m", "trailer_width_m", "trailer_length_m", "trailer_plate_number",
	):
		op.drop_column("company_vehicles", name)
	op.drop_column("company_drivers", "inn")
