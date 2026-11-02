"""Carrier integrity: keep accepted shipments, unique numbers, request upsert index.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-11-02
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def _index_exists(name: str) -> bool:
	bind = op.get_bind()
	rows = bind.execute(sa.text("SELECT 1 FROM pg_indexes WHERE indexname = :n"), {"n": name}).fetchone()
	return rows is not None


def upgrade() -> None:
	# Accepted shipments must survive request cleanup / accidental deletes.
	op.execute(
		sa.text(
			"""
			ALTER TABLE shipments
			DROP CONSTRAINT IF EXISTS shipments_request_id_fkey
			"""
		)
	)
	op.execute(
		sa.text(
			"""
			ALTER TABLE shipments
			ADD CONSTRAINT shipments_request_id_fkey
			FOREIGN KEY (request_id) REFERENCES shipment_requests(id) ON DELETE RESTRICT
			"""
		)
	)

	if not _index_exists("uq_shipments_year_number"):
		op.execute(
			sa.text(
				"""
				DELETE FROM shipments a
				USING shipments b
				WHERE a.id > b.id
				  AND a.year = b.year
				  AND a.number = b.number
				"""
			)
		)
		op.create_index("uq_shipments_year_number", "shipments", ["year", "number"], unique=True)

	if not _index_exists("ix_shipment_requests_open_lookup"):
		op.create_index(
			"ix_shipment_requests_open_lookup",
			"shipment_requests",
			["client_company_id", "carrier_company_id", "status"],
		)

	# At most one open (passive/active) request per client↔carrier pair.
	if not _index_exists("uq_shipment_requests_open_pair"):
		op.execute(
			sa.text(
				"""
				DELETE FROM shipment_requests a
				USING shipment_requests b
				WHERE a.id > b.id
				  AND a.client_company_id = b.client_company_id
				  AND a.carrier_company_id = b.carrier_company_id
				  AND a.status IN ('passive', 'active')
				  AND b.status IN ('passive', 'active')
				"""
			)
		)
		op.execute(
			sa.text(
				"""
				CREATE UNIQUE INDEX uq_shipment_requests_open_pair
				ON shipment_requests (client_company_id, carrier_company_id)
				WHERE status IN ('passive', 'active')
				"""
			)
		)


def downgrade() -> None:
	op.execute(sa.text("DROP INDEX IF EXISTS uq_shipment_requests_open_pair"))
	if _index_exists("ix_shipment_requests_open_lookup"):
		op.drop_index("ix_shipment_requests_open_lookup", table_name="shipment_requests")
	if _index_exists("uq_shipments_year_number"):
		op.drop_index("uq_shipments_year_number", table_name="shipments")
	op.execute(sa.text("ALTER TABLE shipments DROP CONSTRAINT IF EXISTS shipments_request_id_fkey"))
	op.execute(
		sa.text(
			"""
			ALTER TABLE shipments
			ADD CONSTRAINT shipments_request_id_fkey
			FOREIGN KEY (request_id) REFERENCES shipment_requests(id) ON DELETE CASCADE
			"""
		)
	)
