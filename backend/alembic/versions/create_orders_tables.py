"""Create orders tables

Revision ID: create_orders_tables
Revises: b81e833cc420
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'create_orders_tables'
down_revision: Union[str, None] = 'b81e833cc420'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Проверяем существование таблицы units_of_measurement и создаем только если её нет
    if not op.get_bind().execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'units_of_measurement')")).scalar():
        op.create_table('units_of_measurement',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('symbol', sa.String(length=20), nullable=False),
            sa.Column('code', sa.String(length=10), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_units_of_measurement_id'), 'units_of_measurement', ['id'], unique=False)

    # Проверяем существование таблицы orders и создаем только если её нет
    if not op.get_bind().execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'orders')")).scalar():
        op.create_table('orders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('buyer_order_number', sa.String(length=20), nullable=False),
            sa.Column('seller_order_number', sa.String(length=20), nullable=False),
            sa.Column('deal_type', sa.Enum('Товары', 'Услуги', name='ordertype'), nullable=False),
            sa.Column('status', sa.Enum('Активная', 'Завершенная', name='orderstatus'), nullable=False),
            sa.Column('buyer_company_id', sa.Integer(), nullable=False),
            sa.Column('seller_company_id', sa.Integer(), nullable=False),
            sa.Column('invoice_number', sa.String(length=20), nullable=True),
            sa.Column('contract_number', sa.String(length=20), nullable=True),
            sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('contract_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('comments', sa.Text(), nullable=True),
            sa.Column('total_amount', sa.Float(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['buyer_company_id'], ['companies.id'], ),
            sa.ForeignKeyConstraint(['seller_company_id'], ['companies.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)

    # Проверяем существование таблицы order_items и создаем только если её нет
    if not op.get_bind().execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'order_items')")).scalar():
        op.create_table('order_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('product_id', sa.Integer(), nullable=True),
            sa.Column('product_name', sa.String(length=255), nullable=False),
            sa.Column('product_slug', sa.String(length=255), nullable=True),
            sa.Column('product_description', sa.Text(), nullable=True),
            sa.Column('product_article', sa.String(length=100), nullable=True),
            sa.Column('product_type', sa.String(length=50), nullable=True),
            sa.Column('logo_url', sa.String(length=255), nullable=True),
            sa.Column('quantity', sa.Float(), nullable=False),
            sa.Column('unit_of_measurement', sa.String(length=50), nullable=False),
            sa.Column('price', sa.Float(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('position', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
            sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)

    # Проверяем существование таблицы order_history и создаем только если её нет
    if not op.get_bind().execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'order_history')")).scalar():
        op.create_table('order_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('changed_by_company_id', sa.Integer(), nullable=False),
            sa.Column('change_type', sa.String(length=50), nullable=False),
            sa.Column('change_description', sa.Text(), nullable=False),
            sa.Column('old_data', sa.JSON(), nullable=True),
            sa.Column('new_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['changed_by_company_id'], ['companies.id'], ),
            sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_order_history_id'), 'order_history', ['id'], unique=False)

    # Проверяем существование таблицы order_documents и создаем только если её нет
    if not op.get_bind().execute(sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'order_documents')")).scalar():
        op.create_table('order_documents',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('document_type', sa.String(length=50), nullable=False),
            sa.Column('document_number', sa.String(length=50), nullable=False),
            sa.Column('document_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('document_content', sa.JSON(), nullable=True),
            sa.Column('document_file_path', sa.String(length=500), nullable=True),
            sa.Column('is_sent', sa.Boolean(), nullable=False),
            sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_order_documents_id'), 'order_documents', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем таблицы
    op.drop_index(op.f('ix_order_documents_id'), table_name='order_documents')
    op.drop_table('order_documents')
    op.drop_index(op.f('ix_order_history_id'), table_name='order_history')
    op.drop_table('order_history')
    op.drop_index(op.f('ix_order_items_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_units_of_measurement_id'), table_name='units_of_measurement')
    op.drop_table('units_of_measurement')
    
    # Удаляем enum типы
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS ordertype')
