"""transport_document table (ТЗ договор перевозки §1.2)

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-11-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DOC_TYPE_NAME = "transportdocumenttype"
_DOC_TYPE_VALUES = (
	"carriage_contract",
	"carriage_application",
	"carriage_order",
	"expedition_contract",
	"forwarder_assignment",
	"forwarder_receipt",
	"warehouse_receipt",
)


def upgrade() -> None:
	doc_type = postgresql.ENUM(*_DOC_TYPE_VALUES, name=_DOC_TYPE_NAME, create_type=False)
	doc_type.create(op.get_bind(), checkfirst=True)
	op.create_table(
		"transport_document",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("owner_company_id", sa.Integer(), nullable=False),
		sa.Column("carrier_company_id", sa.Integer(), nullable=False),
		sa.Column("doc_type", doc_type, nullable=False),
		sa.Column("number", sa.String(length=32), nullable=False),
		sa.Column("date", sa.DateTime(), nullable=False),
		sa.Column("parent_id", sa.Integer(), nullable=True),
		sa.Column("deal_id", sa.Integer(), nullable=True),
		sa.Column("payload_json", sa.JSON(), nullable=True),
		sa.Column("created_at", sa.DateTime(), nullable=True),
		sa.Column("updated_at", sa.DateTime(), nullable=True),
		sa.ForeignKeyConstraint(["carrier_company_id"], ["companies.id"], ondelete="CASCADE"),
		sa.ForeignKeyConstraint(["owner_company_id"], ["companies.id"], ondelete="CASCADE"),
		sa.ForeignKeyConstraint(["parent_id"], ["transport_document.id"], ondelete="CASCADE"),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index(
		op.f("ix_transport_document_owner_company_id"),
		"transport_document",
		["owner_company_id"],
		unique=False,
	)
	op.create_index(
		op.f("ix_transport_document_carrier_company_id"),
		"transport_document",
		["carrier_company_id"],
		unique=False,
	)
	op.create_index(
		op.f("ix_transport_document_doc_type"),
		"transport_document",
		["doc_type"],
		unique=False,
	)
	op.create_index(
		op.f("ix_transport_document_parent_id"),
		"transport_document",
		["parent_id"],
		unique=False,
	)
	op.create_index(
		op.f("ix_transport_document_deal_id"),
		"transport_document",
		["deal_id"],
		unique=False,
	)
	op.create_index(
		"uq_transport_doc_root_number",
		"transport_document",
		["owner_company_id", "carrier_company_id", "doc_type", "number"],
		unique=True,
		postgresql_where=sa.text("parent_id IS NULL"),
	)
	op.create_index(
		"uq_transport_doc_child_number",
		"transport_document",
		["parent_id", "doc_type", "number"],
		unique=True,
		postgresql_where=sa.text("parent_id IS NOT NULL"),
	)


def downgrade() -> None:
	op.drop_index("uq_transport_doc_child_number", table_name="transport_document")
	op.drop_index("uq_transport_doc_root_number", table_name="transport_document")
	op.drop_index(op.f("ix_transport_document_deal_id"), table_name="transport_document")
	op.drop_index(op.f("ix_transport_document_parent_id"), table_name="transport_document")
	op.drop_index(op.f("ix_transport_document_doc_type"), table_name="transport_document")
	op.drop_index(op.f("ix_transport_document_carrier_company_id"), table_name="transport_document")
	op.drop_index(op.f("ix_transport_document_owner_company_id"), table_name="transport_document")
	op.drop_table("transport_document")
	postgresql.ENUM(name=_DOC_TYPE_NAME).drop(op.get_bind(), checkfirst=True)
