"""empty message

Revision ID: 6c50c32257ff
Revises: d16f14d07843
Create Date: 2025-07-04 14:42:04.361229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c50c32257ff'
down_revision: Union[str, None] = 'd16f14d07843'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    if conn.execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'companies')")).scalar():
        op.alter_column('companies', 'inn',
                   existing_type=sa.VARCHAR(length=12),
                   nullable=True)
        op.alter_column('companies', 'ogrn',
                   existing_type=sa.VARCHAR(length=15),
                   nullable=True)
    if conn.execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'inn')")).scalar():
        op.create_unique_constraint('uq_users_inn', 'users', ['inn'])


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    if conn.execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.table_constraints WHERE table_name = 'users' AND constraint_name = 'uq_users_inn')")).scalar():
        op.drop_constraint('uq_users_inn', 'users', type_='unique')
    if conn.execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'companies')")).scalar():
        op.alter_column('companies', 'ogrn',
                   existing_type=sa.VARCHAR(length=15),
                   nullable=False)
        op.alter_column('companies', 'inn',
                   existing_type=sa.VARCHAR(length=12),
                   nullable=False)
