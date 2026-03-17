"""add bill_officials to orders

Revision ID: bill_officials
Revises: 2bde2926be25
Create Date: 2026-03-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bill_officials"
down_revision: Union[str, None] = "2bde2926be25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column("orders", sa.Column("bill_officials", sa.JSON(), nullable=True))


def downgrade() -> None:
	op.drop_column("orders", "bill_officials")
