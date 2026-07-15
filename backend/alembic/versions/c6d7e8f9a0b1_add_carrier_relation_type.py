"""company_relations: add CARRIER relation type

Revision ID: c6d7e8f9a0b1
Revises: b1c2d3e4f5a6
Create Date: 2026-07-15

"""
from __future__ import annotations

from alembic import op


revision = "c6d7e8f9a0b1"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE companyrelationtype ADD VALUE IF NOT EXISTS 'CARRIER'")


def downgrade() -> None:
    # PostgreSQL: удаление значения enum без пересоздания типа не поддерживается.
    pass
