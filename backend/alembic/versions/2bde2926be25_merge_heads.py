"""merge heads

Revision ID: 2bde2926be25
Revises: add_company_index, order_version_approval
Create Date: 2026-03-16 08:19:14.707954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bde2926be25'
down_revision: Union[str, None] = ('add_company_index', 'order_version_approval')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
