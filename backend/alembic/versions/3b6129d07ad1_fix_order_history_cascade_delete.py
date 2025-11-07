"""fix_order_history_cascade_delete

Revision ID: 3b6129d07ad1
Revises: c52fe6f2fee0
Create Date: 2025-10-25 22:37:30.629512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b6129d07ad1'
down_revision: Union[str, None] = 'c52fe6f2fee0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Исправляем внешний ключ для order_history.changed_by_company_id
    op.drop_constraint('order_history_changed_by_company_id_fkey', 'order_history', type_='foreignkey')
    op.create_foreign_key(
        'order_history_changed_by_company_id_fkey',
        'order_history', 'companies',
        ['changed_by_company_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешний ключ без каскадного удаления
    op.drop_constraint('order_history_changed_by_company_id_fkey', 'order_history', type_='foreignkey')
    op.create_foreign_key(
        'order_history_changed_by_company_id_fkey',
        'order_history', 'companies',
        ['changed_by_company_id'], ['id']
    )
