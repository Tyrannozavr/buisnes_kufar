"""Refactor orders fields: remove invoice, add buyer/seller_order_date, bill, supply_contracts, closing/others_documents

Revision ID: refactor_orders_fields
Revises: bb50c0c0655b
Create Date: 2026-02-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'refactor_orders_fields'
down_revision: Union[str, None] = 'bb50c0c0655b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Refactor order fields."""
    # Add new columns first
    op.add_column('orders', sa.Column('buyer_order_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('seller_order_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('bill_number', sa.String(length=20), nullable=True))
    op.add_column('orders', sa.Column('bill_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('supply_contracts_number', sa.String(length=20), nullable=True))
    op.add_column('orders', sa.Column('supply_contracts_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('orders', sa.Column('closing_documents', sa.JSON(), nullable=True))
    op.add_column('orders', sa.Column('others_documents', sa.JSON(), nullable=True))

    # Drop old columns
    op.drop_column('orders', 'invoice_number')
    op.drop_column('orders', 'invoice_date')


def downgrade() -> None:
    """Revert order fields."""
    op.add_column('orders', sa.Column('invoice_number', sa.String(length=20), nullable=True))
    op.add_column('orders', sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=True))

    op.drop_column('orders', 'others_documents')
    op.drop_column('orders', 'closing_documents')
    op.drop_column('orders', 'supply_contracts_date')
    op.drop_column('orders', 'supply_contracts_number')
    op.drop_column('orders', 'bill_date')
    op.drop_column('orders', 'bill_number')
    op.drop_column('orders', 'seller_order_date')
    op.drop_column('orders', 'buyer_order_date')
