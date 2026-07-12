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
    op.execute("ALTER TABLE companies ADD COLUMN IF NOT EXISTS current_account_number VARCHAR(20)")
    op.execute("ALTER TABLE companies ADD COLUMN IF NOT EXISTS bic VARCHAR(9)")
    op.execute("ALTER TABLE companies ADD COLUMN IF NOT EXISTS vat_rate INTEGER")
    op.execute("ALTER TABLE companies ADD COLUMN IF NOT EXISTS correspondent_bank_account VARCHAR(20)")
    op.execute("ALTER TABLE companies ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255)")


def downgrade() -> None:
    """Remove payment and bank fields from companies table."""
    # Remove bank details / payment information columns
    op.drop_column('companies', 'bank_name')
    op.drop_column('companies', 'correspondent_bank_account')
    op.drop_column('companies', 'vat_rate')
    op.drop_column('companies', 'bic')
    op.drop_column('companies', 'current_account_number')
