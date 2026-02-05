"""add_payment_fields_to_company

Revision ID: bb50c0c0655b
Revises: 210710ff5aef
Create Date: 2026-02-05 09:58:16.291146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb50c0c0655b'
down_revision: Union[str, None] = '210710ff5aef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add payment and bank fields to companies table."""
    # Add bank details / payment information columns
    op.add_column('companies', sa.Column('current_account_number', sa.String(length=20), nullable=True))
    op.add_column('companies', sa.Column('bic', sa.String(length=9), nullable=True))
    op.add_column('companies', sa.Column('vat_rate', sa.Integer(), nullable=True))
    op.add_column('companies', sa.Column('correspondent_bank_account', sa.String(length=20), nullable=True))
    op.add_column('companies', sa.Column('bank_name', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove payment and bank fields from companies table."""
    # Remove bank details / payment information columns
    op.drop_column('companies', 'bank_name')
    op.drop_column('companies', 'correspondent_bank_account')
    op.drop_column('companies', 'vat_rate')
    op.drop_column('companies', 'bic')
    op.drop_column('companies', 'current_account_number')
