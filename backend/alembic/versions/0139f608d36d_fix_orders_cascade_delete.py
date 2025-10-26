"""fix_orders_cascade_delete

Revision ID: 0139f608d36d
Revises: 7006a9b34257
Create Date: 2025-10-25 22:31:08.974225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0139f608d36d'
down_revision: Union[str, None] = '7006a9b34257'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем существующие внешние ключи для orders
    op.drop_constraint('orders_buyer_company_id_fkey', 'orders', type_='foreignkey')
    op.drop_constraint('orders_seller_company_id_fkey', 'orders', type_='foreignkey')
    
    # Создаем новые внешние ключи с каскадным удалением
    op.create_foreign_key(
        'orders_buyer_company_id_fkey',
        'orders', 'companies',
        ['buyer_company_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'orders_seller_company_id_fkey',
        'orders', 'companies',
        ['seller_company_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешние ключи без каскадного удаления
    op.drop_constraint('orders_buyer_company_id_fkey', 'orders', type_='foreignkey')
    op.drop_constraint('orders_seller_company_id_fkey', 'orders', type_='foreignkey')
    
    op.create_foreign_key(
        'orders_buyer_company_id_fkey',
        'orders', 'companies',
        ['buyer_company_id'], ['id']
    )
    op.create_foreign_key(
        'orders_seller_company_id_fkey',
        'orders', 'companies',
        ['seller_company_id'], ['id']
    )
