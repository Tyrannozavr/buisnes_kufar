"""fix_order_items_cascade_delete

Revision ID: 8bac79b4f376
Revises: 3b6129d07ad1
Create Date: 2025-10-25 22:37:49.694529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bac79b4f376'
down_revision: Union[str, None] = '3b6129d07ad1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    has_order_id = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'order_items' AND column_name = 'order_id')"
        )
    ).scalar()
    if not has_order_id:
        return

    op.execute('ALTER TABLE order_items DROP CONSTRAINT IF EXISTS order_items_order_id_fkey')
    op.create_foreign_key(
        'order_items_order_id_fkey',
        'order_items', 'orders',
        ['order_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешний ключ без каскадного удаления
    op.drop_constraint('order_items_order_id_fkey', 'order_items', type_='foreignkey')
    op.create_foreign_key(
        'order_items_order_id_fkey',
        'order_items', 'orders',
        ['order_id'], ['id']
    )
