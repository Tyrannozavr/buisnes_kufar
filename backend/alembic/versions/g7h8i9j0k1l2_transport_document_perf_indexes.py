"""transport_document perf indexes (picker + numbering)

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-11-02

По отчёту DB-тестировщика: составные индексы под list_for_picker и нумерацию корней.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.execute(
		"""
		CREATE INDEX IF NOT EXISTS ix_transport_doc_picker
		ON transport_document (owner_company_id, carrier_company_id, doc_type, date DESC, id DESC)
		WHERE parent_id IS NULL
		"""
	)
	op.execute(
		"""
		CREATE INDEX IF NOT EXISTS ix_transport_doc_root_numbering
		ON transport_document (owner_company_id, carrier_company_id, doc_type, date)
		WHERE parent_id IS NULL
		"""
	)
	op.execute(
		"""
		CREATE INDEX IF NOT EXISTS ix_transport_doc_owner_deal
		ON transport_document (owner_company_id, deal_id)
		WHERE deal_id IS NOT NULL
		"""
	)


def downgrade() -> None:
	op.execute("DROP INDEX IF EXISTS ix_transport_doc_owner_deal")
	op.execute("DROP INDEX IF EXISTS ix_transport_doc_root_numbering")
	op.execute("DROP INDEX IF EXISTS ix_transport_doc_picker")
