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
    # Удаляем существующие foreign key constraints
    op.drop_constraint('employees_created_by_fkey', 'employees', type_='foreignkey')
    op.drop_constraint('employees_user_id_fkey', 'employees', type_='foreignkey')
    op.drop_constraint('employees_company_id_fkey', 'employees', type_='foreignkey')
    
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
    op.drop_constraint('users_company_id_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(
        'users_company_id_fkey',
        'users', 'companies',
        ['company_id'], ['id'],
        ondelete='SET NULL'
    )
    
    op.drop_constraint('company_officials_company_id_fkey', 'company_officials', type_='foreignkey')
    op.create_foreign_key(
        'company_officials_company_id_fkey',
        'company_officials', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем старые constraints без CASCADE
    op.drop_constraint('employees_created_by_fkey', 'employees', type_='foreignkey')
    op.drop_constraint('employees_user_id_fkey', 'employees', type_='foreignkey')
    op.drop_constraint('employees_company_id_fkey', 'employees', type_='foreignkey')
    
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
    
    op.drop_constraint('users_company_id_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(
        'users_company_id_fkey',
        'users', 'companies',
        ['company_id'], ['id']
    )
    
    op.drop_constraint('company_officials_company_id_fkey', 'company_officials', type_='foreignkey')
    op.create_foreign_key(
        'company_officials_company_id_fkey',
        'company_officials', 'companies',
        ['company_id'], ['id']
    )
