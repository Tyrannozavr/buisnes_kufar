"""Add order version approval fields (proposed_by, accepted, rejected)

Revision ID: order_version_approval
Revises: doc_form_ver
Create Date: 2026-02-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "order_version_approval"
down_revision: Union[str, None] = "doc_form_ver"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("proposed_by_company_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("buyer_accepted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("seller_accepted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("rejected_by_company_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_orders_proposed_by_company",
        "orders",
        "companies",
        ["proposed_by_company_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_orders_rejected_by_company",
        "orders",
        "companies",
        ["rejected_by_company_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_orders_rejected_by_company", "orders", type_="foreignkey")
    op.drop_constraint("fk_orders_proposed_by_company", "orders", type_="foreignkey")
    op.drop_column("orders", "rejected_by_company_id")
    op.drop_column("orders", "seller_accepted_at")
    op.drop_column("orders", "buyer_accepted_at")
    op.drop_column("orders", "proposed_by_company_id")
