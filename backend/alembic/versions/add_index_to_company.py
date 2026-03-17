"""add index to company

Revision ID: add_company_index
Revises: doc_form_ver
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_company_index"
down_revision: Union[str, None] = "doc_form_ver"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column("companies", sa.Column("index", sa.String(length=10), nullable=True))


def downgrade() -> None:
	op.drop_column("companies", "index")
