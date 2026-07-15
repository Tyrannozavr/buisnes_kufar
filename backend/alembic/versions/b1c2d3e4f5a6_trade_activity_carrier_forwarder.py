"""trade_activity: Производитель / Продавец / Перевозчик / Экспедитор

Revision ID: b1c2d3e4f5a6
Revises: a4b5c6d7e8f9
Create Date: 2026-07-15

Маппинг старых значений: BUYER, BOTH → SELLER.
"""
from __future__ import annotations

from alembic import op


revision = "b1c2d3e4f5a6"
down_revision = "a4b5c6d7e8f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL: нельзя удалить label из enum — пересоздаём тип.
    op.execute(
        """
        UPDATE companies
        SET trade_activity = 'SELLER'
        WHERE trade_activity::text IN ('BUYER', 'BOTH')
        """
    )
    op.execute("ALTER TYPE tradeactivity RENAME TO tradeactivity_old")
    op.execute(
        "CREATE TYPE tradeactivity AS ENUM "
        "('PRODUCER', 'SELLER', 'CARRIER', 'FORWARDER')"
    )
    op.execute(
        """
        ALTER TABLE companies
        ALTER COLUMN trade_activity TYPE tradeactivity
        USING trade_activity::text::tradeactivity
        """
    )
    op.execute("DROP TYPE tradeactivity_old")


def downgrade() -> None:
    op.execute(
        """
        UPDATE companies
        SET trade_activity = 'SELLER'
        WHERE trade_activity::text IN ('PRODUCER', 'CARRIER', 'FORWARDER')
        """
    )
    op.execute("ALTER TYPE tradeactivity RENAME TO tradeactivity_new")
    op.execute(
        "CREATE TYPE tradeactivity AS ENUM ('BUYER', 'SELLER', 'BOTH')"
    )
    op.execute(
        """
        ALTER TABLE companies
        ALTER COLUMN trade_activity TYPE tradeactivity
        USING trade_activity::text::tradeactivity
        """
    )
    op.execute("DROP TYPE tradeactivity_new")
