"""add email_notifications_enabled to users

Revision ID: a1b2c3d4e5f6
Revises: f9b0c1d2e3f4
Create Date: 2026-07-17 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f9b0c1d2e3f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users "
        "ADD COLUMN IF NOT EXISTS email_notifications_enabled BOOLEAN NOT NULL DEFAULT FALSE"
    )


def downgrade() -> None:
    op.drop_column("users", "email_notifications_enabled")
