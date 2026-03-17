"""Remove buyer_order_date, seller_order_date from orders

Revision ID: remove_order_dates
Revises:
Create Date:

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "remove_order_dates"
down_revision = "2bde2926be25"
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.drop_column("orders", "buyer_order_date")
	op.drop_column("orders", "seller_order_date")


def downgrade() -> None:
	op.add_column("orders", sa.Column("buyer_order_date", sa.DateTime(timezone=True), nullable=True))
	op.add_column("orders", sa.Column("seller_order_date", sa.DateTime(timezone=True), nullable=True))
