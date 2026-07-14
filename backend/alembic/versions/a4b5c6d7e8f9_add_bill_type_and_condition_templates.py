"""add bill_document_type and contract_condition_templates

Revision ID: a4b5c6d7e8f9
Revises: f3a8c1d2e4b5
Create Date: 2026-07-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4b5c6d7e8f9"
down_revision: Union[str, None] = "f3a8c1d2e4b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	# IF NOT EXISTS: безопасный upgrade после SQLAlchemy create_all на пустой dev-БД
	op.execute(
		"""
		ALTER TABLE orders
		ADD COLUMN IF NOT EXISTS bill_document_type VARCHAR(32) NOT NULL DEFAULT 'bill'
		"""
	)
	op.execute(
		"""
		ALTER TABLE orders
		ADD COLUMN IF NOT EXISTS bill_supplier_details_check BOOLEAN NOT NULL DEFAULT true
		"""
	)
	op.execute(
		"""
		ALTER TABLE orders
		ADD COLUMN IF NOT EXISTS bill_buyer_details_check BOOLEAN NOT NULL DEFAULT true
		"""
	)

	op.execute(
		"""
		CREATE TABLE IF NOT EXISTS contract_condition_template (
			id SERIAL PRIMARY KEY,
			company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
			type VARCHAR(32) NOT NULL,
			name VARCHAR(128) NOT NULL,
			content_text TEXT NOT NULL,
			is_default BOOLEAN NOT NULL DEFAULT false,
			created_at TIMESTAMP WITHOUT TIME ZONE,
			updated_at TIMESTAMP WITHOUT TIME ZONE,
			CONSTRAINT uq_contract_condition_template_company_type_name
				UNIQUE (company_id, type, name)
		)
		"""
	)
	op.execute(
		"CREATE INDEX IF NOT EXISTS ix_contract_condition_template_company_id "
		"ON contract_condition_template (company_id)"
	)
	op.execute(
		"CREATE INDEX IF NOT EXISTS ix_contract_condition_template_type "
		"ON contract_condition_template (type)"
	)


def downgrade() -> None:
	op.drop_index(op.f("ix_contract_condition_template_type"), table_name="contract_condition_template")
	op.drop_index(op.f("ix_contract_condition_template_company_id"), table_name="contract_condition_template")
	op.drop_table("contract_condition_template")
	op.drop_column("orders", "bill_buyer_details_check")
	op.drop_column("orders", "bill_supplier_details_check")
	op.drop_column("orders", "bill_document_type")
