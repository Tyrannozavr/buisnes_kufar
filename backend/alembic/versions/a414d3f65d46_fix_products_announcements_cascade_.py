"""fix_products_announcements_cascade_delete

Revision ID: a414d3f65d46
Revises: a5852840b8ea
Create Date: 2025-10-25 22:31:35.103003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a414d3f65d46'
down_revision: Union[str, None] = 'a5852840b8ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Исправляем внешние ключи для products
    op.drop_constraint('products_company_id_fkey', 'products', type_='foreignkey')
    op.create_foreign_key(
        'products_company_id_fkey',
        'products', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Исправляем внешние ключи для announcements
    op.drop_constraint('announcements_company_id_fkey', 'announcements', type_='foreignkey')
    op.create_foreign_key(
        'announcements_company_id_fkey',
        'announcements', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешние ключи без каскадного удаления для products
    op.drop_constraint('products_company_id_fkey', 'products', type_='foreignkey')
    op.create_foreign_key(
        'products_company_id_fkey',
        'products', 'companies',
        ['company_id'], ['id']
    )
    
    # Возвращаем внешние ключи без каскадного удаления для announcements
    op.drop_constraint('announcements_company_id_fkey', 'announcements', type_='foreignkey')
    op.create_foreign_key(
        'announcements_company_id_fkey',
        'announcements', 'companies',
        ['company_id'], ['id']
    )
