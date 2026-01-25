"""fix_cascade_delete_constraints

Revision ID: 210710ff5aef
Revises: dbbcb4d5aac3
Create Date: 2025-10-26 00:07:58.179527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '210710ff5aef'
down_revision: Union[str, None] = 'dbbcb4d5aac3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    def _drop_fk_if_exists(table: str, constraint_name: str) -> None:
        # На разных окружениях constraint может отсутствовать (или иметь иное имя),
        # поэтому делаем миграцию идемпотентной по имени constraint.
        op.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{constraint_name}"')

    # Удаляем существующие foreign key constraints
    _drop_fk_if_exists('employees', 'employees_created_by_fkey')
    _drop_fk_if_exists('employees', 'employees_user_id_fkey')
    _drop_fk_if_exists('employees', 'employees_company_id_fkey')
    
    # Создаем новые constraints с CASCADE DELETE
    op.create_foreign_key(
        'employees_created_by_fkey',
        'employees', 'users',
        ['created_by'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'employees_user_id_fkey',
        'employees', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'employees_company_id_fkey',
        'employees', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Также настроим CASCADE для других таблиц
    _drop_fk_if_exists('users', 'users_company_id_fkey')
    op.create_foreign_key(
        'users_company_id_fkey',
        'users', 'companies',
        ['company_id'], ['id'],
        ondelete='SET NULL'
    )
    
    _drop_fk_if_exists('company_officials', 'company_officials_company_id_fkey')
    op.create_foreign_key(
        'company_officials_company_id_fkey',
        'company_officials', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    def _drop_fk_if_exists(table: str, constraint_name: str) -> None:
        op.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{constraint_name}"')

    # Возвращаем старые constraints без CASCADE
    _drop_fk_if_exists('employees', 'employees_created_by_fkey')
    _drop_fk_if_exists('employees', 'employees_user_id_fkey')
    _drop_fk_if_exists('employees', 'employees_company_id_fkey')
    
    op.create_foreign_key(
        'employees_created_by_fkey',
        'employees', 'users',
        ['created_by'], ['id']
    )
    op.create_foreign_key(
        'employees_user_id_fkey',
        'employees', 'users',
        ['user_id'], ['id']
    )
    op.create_foreign_key(
        'employees_company_id_fkey',
        'employees', 'companies',
        ['company_id'], ['id']
    )
    
    _drop_fk_if_exists('users', 'users_company_id_fkey')
    op.create_foreign_key(
        'users_company_id_fkey',
        'users', 'companies',
        ['company_id'], ['id']
    )
    
    _drop_fk_if_exists('company_officials', 'company_officials_company_id_fkey')
    op.create_foreign_key(
        'company_officials_company_id_fkey',
        'company_officials', 'companies',
        ['company_id'], ['id']
    )
