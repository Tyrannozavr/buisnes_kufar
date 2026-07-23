"""Performance indexes for hot FK filters and chat/message lookups.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-23
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def _index_exists(name: str) -> bool:
	bind = op.get_bind()
	rows = bind.execute(sa.text("SELECT 1 FROM pg_indexes WHERE indexname = :n"), {"n": name}).fetchone()
	return rows is not None


def _create_index(name: str, table: str, columns: list[str], *, unique: bool = False) -> None:
	if _index_exists(name):
		return
	op.create_index(name, table, columns, unique=unique)


def upgrade() -> None:
	_create_index("ix_orders_buyer_updated", "orders", ["buyer_company_id", "updated_at"])
	_create_index("ix_orders_seller_updated", "orders", ["seller_company_id", "updated_at"])
	_create_index("ix_order_items_order_row_id", "order_items", ["order_row_id"])
	_create_index(
		"ix_company_relations_lookup",
		"company_relations",
		["company_id", "relation_type", "related_company_id"],
	)
	if not _index_exists("uq_company_relations"):
		op.execute(
			sa.text(
				"""
				DELETE FROM company_relations a
				USING company_relations b
				WHERE a.id > b.id
				  AND a.company_id = b.company_id
				  AND a.related_company_id = b.related_company_id
				  AND a.relation_type = b.relation_type
				"""
			)
		)
		_create_index(
			"uq_company_relations",
			"company_relations",
			["company_id", "related_company_id", "relation_type"],
			unique=True,
		)
	_create_index("ix_messages_chat_created", "messages", ["chat_id", "created_at"])
	_create_index("ix_messages_unread", "messages", ["chat_id", "is_read", "sender_company_id"])
	_create_index("ix_chat_participants_user", "chat_participants", ["user_id"])
	_create_index("ix_chat_participants_company", "chat_participants", ["company_id"])
	if not _index_exists("uq_chat_participant_chat_company"):
		op.execute(
			sa.text(
				"""
				DELETE FROM chat_participants a
				USING chat_participants b
				WHERE a.id > b.id
				  AND a.chat_id = b.chat_id
				  AND a.company_id = b.company_id
				"""
			)
		)
		_create_index(
			"uq_chat_participant_chat_company",
			"chat_participants",
			["chat_id", "company_id"],
			unique=True,
		)
	_create_index("ix_users_company_id", "users", ["company_id"])
	_create_index("ix_companies_trade_activity", "companies", ["trade_activity"])
	_create_index(
		"ix_company_vehicles_search",
		"company_vehicles",
		["is_active", "body_type", "capacity_tons", "volume_m3"],
	)
	_create_index("ix_products_company_type", "products", ["company_id", "type"])
	_create_index("ix_shipments_deal_id", "shipments", ["deal_id"])
	try:
		op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
		if not _index_exists("ix_products_name_trgm"):
			op.execute(
				sa.text(
					"CREATE INDEX ix_products_name_trgm ON products USING gin (name gin_trgm_ops)"
				)
			)
	except Exception:
		pass


def downgrade() -> None:
	for name in (
		"ix_products_name_trgm",
		"ix_shipments_deal_id",
		"ix_products_company_type",
		"ix_company_vehicles_search",
		"ix_companies_trade_activity",
		"ix_users_company_id",
		"uq_chat_participant_chat_company",
		"ix_chat_participants_company",
		"ix_chat_participants_user",
		"ix_messages_unread",
		"ix_messages_chat_created",
		"uq_company_relations",
		"ix_company_relations_lookup",
		"ix_order_items_order_row_id",
		"ix_orders_seller_updated",
		"ix_orders_buyer_updated",
	):
		if _index_exists(name):
			op.drop_index(name)
