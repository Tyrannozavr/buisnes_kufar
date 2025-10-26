"""Update user company relationship

Revision ID: update_user_company_relationship
Revises: create_orders_tables
Create Date: 2025-10-25 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_user_company_relationship'
down_revision: Union[str, None] = 'create_orders_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем новые поля в таблицу users
    op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'USER', name='userrole'), nullable=False, server_default='USER'))
    op.add_column('users', sa.Column('permissions', sa.Text(), nullable=True))
    
    # Добавляем внешний ключ для company_id
    op.create_foreign_key('fk_users_company_id', 'users', 'companies', ['company_id'], ['id'])
    
    # Удаляем поле user_id из таблицы companies
    op.drop_constraint('companies_user_id_fkey', 'companies', type_='foreignkey')
    op.drop_column('companies', 'user_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем поле user_id в таблицу companies
    op.add_column('companies', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('companies_user_id_fkey', 'companies', 'users', ['user_id'], ['id'])
    
    # Удаляем новые поля из таблицы users
    op.drop_constraint('fk_users_company_id', 'users', type_='foreignkey')
    op.drop_column('users', 'permissions')
    op.drop_column('users', 'role')
    op.drop_column('users', 'company_id')
    
    # Enum тип не удаляем, так как он может использоваться другими таблицами
