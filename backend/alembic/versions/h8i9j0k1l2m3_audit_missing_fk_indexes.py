"""Add missing FK / hot-path indexes from DB audit.

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-11-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def _index_exists(name: str) -> bool:
	bind = op.get_bind()
	rows = bind.execute(sa.text("SELECT 1 FROM pg_indexes WHERE indexname = :n"), {"n": name}).fetchone()
	return rows is not None


def _table_exists(name: str) -> bool:
	bind = op.get_bind()
	rows = bind.execute(
		sa.text("SELECT 1 FROM information_schema.tables WHERE table_name = :n"),
		{"n": name},
	).fetchone()
	return rows is not None


def _create_index(name: str, table: str, columns: list[str]) -> None:
	if not _table_exists(table) or _index_exists(name):
		return
	op.create_index(name, table, columns)


def upgrade() -> None:
	_create_index("ix_order_history_order_row_id", "order_history", ["order_row_id"])
	_create_index("ix_order_documents_order_row_id", "order_documents", ["order_row_id"])
	_create_index("ix_company_officials_company_id", "company_officials", ["company_id"])
	_create_index("ix_companies_city_id", "companies", ["city_id"])
	_create_index("ix_announcements_company_id", "announcements", ["company_id"])
	_create_index("ix_employees_company_id", "employees", ["company_id"])
	_create_index("ix_employees_user_id", "employees", ["user_id"])
	_create_index("ix_employee_permissions_employee_id", "employee_permissions", ["employee_id"])
	_create_index("ix_order_items_product_id", "order_items", ["product_id"])
	_create_index("ix_shipments_vehicle_id", "shipments", ["vehicle_id"])
	_create_index("ix_shipments_driver_id", "shipments", ["driver_id"])
	_create_index(
		"ix_company_relations_related",
		"company_relations",
		["related_company_id", "relation_type"],
	)
	_create_index(
		"ix_products_company_type_flags",
		"products",
		["company_id", "type", "is_deleted", "is_hidden"],
	)
	_create_index("ix_cities_region_id", "cities", ["region_id"])
	_create_index("ix_cities_country_id", "cities", ["country_id"])


def downgrade() -> None:
	for name in (
		"ix_cities_country_id",
		"ix_cities_region_id",
		"ix_products_company_type_flags",
		"ix_company_relations_related",
		"ix_shipments_driver_id",
		"ix_shipments_vehicle_id",
		"ix_order_items_product_id",
		"ix_employee_permissions_employee_id",
		"ix_employees_user_id",
		"ix_employees_company_id",
		"ix_announcements_company_id",
		"ix_companies_city_id",
		"ix_company_officials_company_id",
		"ix_order_documents_order_row_id",
		"ix_order_history_order_row_id",
	):
		if _index_exists(name):
			op.drop_index(name)
