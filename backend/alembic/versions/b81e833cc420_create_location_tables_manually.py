"""Create location tables manually

Revision ID: b81e833cc420
Revises: 2ad4670bb348
Create Date: 2025-10-22 19:15:45.579370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b81e833cc420'
down_revision: Union[str, None] = '2ad4670bb348'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу countries
    op.create_table('countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_countries_id'), 'countries', ['id'], unique=False)

    # Создаем таблицу federal_districts
    op.create_table('federal_districts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_federal_districts_id'), 'federal_districts', ['id'], unique=False)

    # Создаем таблицу regions
    op.create_table('regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('federal_district_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
        sa.ForeignKeyConstraint(['federal_district_id'], ['federal_districts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regions_id'), 'regions', ['id'], unique=False)

    # Создаем таблицу cities
    op.create_table('cities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('federal_district_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('is_million_city', sa.Boolean(), nullable=False),
        sa.Column('is_regional_center', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
        sa.ForeignKeyConstraint(['federal_district_id'], ['federal_districts.id'], ),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cities_id'), 'cities', ['id'], unique=False)

    # Добавляем FK поля в таблицу companies
    op.add_column('companies', sa.Column('country_id', sa.Integer(), nullable=True))
    op.add_column('companies', sa.Column('federal_district_id', sa.Integer(), nullable=True))
    op.add_column('companies', sa.Column('region_id', sa.Integer(), nullable=True))
    op.add_column('companies', sa.Column('city_id', sa.Integer(), nullable=True))
    
    # Создаем FK constraints для companies
    op.create_foreign_key('fk_companies_country_id', 'companies', 'countries', ['country_id'], ['id'])
    op.create_foreign_key('fk_companies_federal_district_id', 'companies', 'federal_districts', ['federal_district_id'], ['id'])
    op.create_foreign_key('fk_companies_region_id', 'companies', 'regions', ['region_id'], ['id'])
    op.create_foreign_key('fk_companies_city_id', 'companies', 'cities', ['city_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем FK constraints
    op.drop_constraint('fk_companies_city_id', 'companies', type_='foreignkey')
    op.drop_constraint('fk_companies_region_id', 'companies', type_='foreignkey')
    op.drop_constraint('fk_companies_federal_district_id', 'companies', type_='foreignkey')
    op.drop_constraint('fk_companies_country_id', 'companies', type_='foreignkey')
    
    # Удаляем FK поля из companies
    op.drop_column('companies', 'city_id')
    op.drop_column('companies', 'region_id')
    op.drop_column('companies', 'federal_district_id')
    op.drop_column('companies', 'country_id')
    
    # Удаляем таблицы
    op.drop_index(op.f('ix_cities_id'), table_name='cities')
    op.drop_table('cities')
    op.drop_index(op.f('ix_regions_id'), table_name='regions')
    op.drop_table('regions')
    op.drop_index(op.f('ix_federal_districts_id'), table_name='federal_districts')
    op.drop_table('federal_districts')
    op.drop_index(op.f('ix_countries_id'), table_name='countries')
    op.drop_table('countries')

