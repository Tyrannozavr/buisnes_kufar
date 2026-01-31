"""add deal_document_forms table

Revision ID: e8a1b2c3d4e5
Revises: 210710ff5aef
Create Date: 2026-01-31

Таблица для payload форм редактора документов (заказ, счёт, договор и т.д.).
Одна запись на (deal_id, document_type). updated_by_company_id — для диалога «Контрагент изменил данные».
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = 'e8a1b2c3d4e5'
down_revision: Union[str, None] = '210710ff5aef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'deal_document_forms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deal_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('payload', JSONB(), nullable=False, server_default='{}'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_by_company_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['deal_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by_company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('deal_id', 'document_type', name='uq_deal_document_type'),
    )
    op.create_index('ix_deal_document_forms_deal_id', 'deal_document_forms', ['deal_id'], unique=False)
    op.create_index('ix_deal_document_forms_document_type', 'deal_document_forms', ['document_type'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_deal_document_forms_document_type', table_name='deal_document_forms')
    op.drop_index('ix_deal_document_forms_deal_id', table_name='deal_document_forms')
    op.drop_table('deal_document_forms')
