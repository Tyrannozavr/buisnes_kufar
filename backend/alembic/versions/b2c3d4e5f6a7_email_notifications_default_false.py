"""email_notifications_enabled default false

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-17 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN email_notifications_enabled SET DEFAULT FALSE"
    )
    # Колонка только что появилась с DEFAULT TRUE — сбрасываем на выключено
    op.execute("UPDATE users SET email_notifications_enabled = FALSE")


def downgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN email_notifications_enabled SET DEFAULT TRUE"
    )
