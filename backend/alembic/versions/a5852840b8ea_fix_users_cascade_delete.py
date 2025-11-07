"""fix_users_cascade_delete

Revision ID: a5852840b8ea
Revises: 0139f608d36d
Create Date: 2025-10-25 22:31:24.253636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5852840b8ea'
down_revision: Union[str, None] = '0139f608d36d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем существующий внешний ключ для users.company_id
    op.drop_constraint('fk_users_company_id', 'users', type_='foreignkey')
    
    # Создаем новый внешний ключ с каскадным удалением
    op.create_foreign_key(
        'fk_users_company_id',
        'users', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешний ключ без каскадного удаления
    op.drop_constraint('fk_users_company_id', 'users', type_='foreignkey')
    
    op.create_foreign_key(
        'fk_users_company_id',
        'users', 'companies',
        ['company_id'], ['id']
    )
