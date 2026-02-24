"""add document form version and updated_by to order_documents

Revision ID: doc_form_ver
Revises: 9f4e8d7c1a2b
Create Date: 2026-02-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "doc_form_ver"
down_revision: Union[str, None] = "9f4e8d7c1a2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "order_documents",
        sa.Column("document_version", sa.String(20), nullable=False, server_default="v1"),
    )
    op.add_column(
        "order_documents",
        sa.Column("updated_by_company_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_order_documents_updated_by_company",
        "order_documents",
        "companies",
        ["updated_by_company_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_order_documents_updated_by_company",
        "order_documents",
        type_="foreignkey",
    )
    op.drop_column("order_documents", "updated_by_company_id")
    op.drop_column("order_documents", "document_version")
