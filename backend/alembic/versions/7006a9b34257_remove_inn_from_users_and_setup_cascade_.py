"""remove_inn_from_users_and_setup_cascade_delete

Revision ID: 7006a9b34257
Revises: update_user_company_relationship
Create Date: 2025-10-25 22:06:43.554130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7006a9b34257'
down_revision: Union[str, None] = 'update_user_company_relationship'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем поле inn из таблицы users
    op.drop_column('users', 'inn')
    
    # Удаляем внешний ключ employees_user_id_fkey
    op.drop_constraint('employees_user_id_fkey', 'employees', type_='foreignkey')
    
    # Создаем новый внешний ключ с каскадным удалением
    op.create_foreign_key(
        'employees_user_id_fkey',
        'employees', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешний ключ без каскадного удаления
    op.drop_constraint('employees_user_id_fkey', 'employees', type_='foreignkey')
    op.create_foreign_key(
        'employees_user_id_fkey',
        'employees', 'users',
        ['user_id'], ['id']
    )
    
    # Возвращаем поле inn в таблицу users
    op.add_column('users', sa.Column('inn', sa.String(), nullable=True))
