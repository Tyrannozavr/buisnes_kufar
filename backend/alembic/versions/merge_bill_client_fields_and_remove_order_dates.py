"""merge bill client fields and remove order dates heads

Revision ID: merge_bill_heads
Revises: bill_client_fields, remove_order_dates
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "merge_bill_heads"
down_revision: Union[str, tuple[str, str], None] = ("bill_client_fields", "remove_order_dates")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	pass


def downgrade() -> None:
	pass
