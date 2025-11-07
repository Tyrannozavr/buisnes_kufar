"""fix_chats_messages_cascade_delete

Revision ID: c52fe6f2fee0
Revises: a414d3f65d46
Create Date: 2025-10-25 22:31:49.304136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c52fe6f2fee0'
down_revision: Union[str, None] = 'a414d3f65d46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Исправляем внешние ключи для messages
    op.drop_constraint('messages_sender_company_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key(
        'messages_sender_company_id_fkey',
        'messages', 'companies',
        ['sender_company_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Исправляем внешние ключи для chat_participants
    op.drop_constraint('chat_participants_company_id_fkey', 'chat_participants', type_='foreignkey')
    op.create_foreign_key(
        'chat_participants_company_id_fkey',
        'chat_participants', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем внешние ключи без каскадного удаления для messages
    op.drop_constraint('messages_sender_company_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key(
        'messages_sender_company_id_fkey',
        'messages', 'companies',
        ['sender_company_id'], ['id']
    )
    
    # Возвращаем внешние ключи без каскадного удаления для chat_participants
    op.drop_constraint('chat_participants_company_id_fkey', 'chat_participants', type_='foreignkey')
    op.create_foreign_key(
        'chat_participants_company_id_fkey',
        'chat_participants', 'companies',
        ['company_id'], ['id']
    )
