"""fix_order_documents_cascade_delete

Revision ID: dbbcb4d5aac3
Revises: 8bac79b4f376
Create Date: 2025-10-25 22:38:16.114908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbbcb4d5aac3'
down_revision: Union[str, None] = '8bac79b4f376'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Исправляем внешний ключ для order_documents.order_id
    op.drop_constraint('order_documents_order_id_fkey', 'order_documents', type_='foreignkey')
    op.create_foreign_key(
        'order_documents_order_id_fkey',
        'order_documents', 'orders',
        ['order_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешний ключ без каскадного удаления
    op.drop_constraint('order_documents_order_id_fkey', 'order_documents', type_='foreignkey')
    op.create_foreign_key(
        'order_documents_order_id_fkey',
        'order_documents', 'orders',
        ['order_id'], ['id']
    )
