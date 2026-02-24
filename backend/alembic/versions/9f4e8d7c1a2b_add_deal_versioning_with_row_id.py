"""Add deal versioning with stable deal id and row_id PK

Revision ID: 9f4e8d7c1a2b
Revises: refactor_orders_fields
Create Date: 2026-02-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f4e8d7c1a2b"
down_revision: Union[str, None] = "refactor_orders_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) Orders: add technical PK and versioning columns.
    op.add_column("orders", sa.Column("row_id", sa.Integer(), nullable=True))
    op.add_column(
        "orders",
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )

    # Create and backfill row_id for existing records.
    op.execute("CREATE SEQUENCE IF NOT EXISTS orders_row_id_seq")
    op.execute(
        "ALTER TABLE orders ALTER COLUMN row_id SET DEFAULT nextval('orders_row_id_seq')"
    )
    op.execute("UPDATE orders SET row_id = nextval('orders_row_id_seq') WHERE row_id IS NULL")
    op.alter_column("orders", "row_id", nullable=False)

    # Keep sequence in sync.
    op.execute(
        "SELECT setval('orders_row_id_seq', COALESCE((SELECT MAX(row_id) FROM orders), 1), true)"
    )
    op.create_unique_constraint("uq_orders_row_id", "orders", ["row_id"])

    # 2) Child tables: add order_row_id and backfill from current order_id -> orders.id mapping.
    op.add_column("order_items", sa.Column("order_row_id", sa.Integer(), nullable=True))
    op.add_column("order_history", sa.Column("order_row_id", sa.Integer(), nullable=True))
    op.add_column("order_documents", sa.Column("order_row_id", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE order_items oi
        SET order_row_id = o.row_id
        FROM orders o
        WHERE oi.order_id = o.id
        """
    )
    op.execute(
        """
        UPDATE order_history oh
        SET order_row_id = o.row_id
        FROM orders o
        WHERE oh.order_id = o.id
        """
    )
    op.execute(
        """
        UPDATE order_documents od
        SET order_row_id = o.row_id
        FROM orders o
        WHERE od.order_id = o.id
        """
    )

    # Drop old FK constraints to orders.id.
    op.execute("ALTER TABLE order_items DROP CONSTRAINT IF EXISTS order_items_order_id_fkey")
    op.execute("ALTER TABLE order_history DROP CONSTRAINT IF EXISTS order_history_order_id_fkey")
    op.execute(
        "ALTER TABLE order_documents DROP CONSTRAINT IF EXISTS order_documents_order_id_fkey"
    )

    # Create new FK constraints to orders.row_id.
    op.create_foreign_key(
        "fk_order_items_order_row_id_orders",
        "order_items",
        "orders",
        ["order_row_id"],
        ["row_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_order_history_order_row_id_orders",
        "order_history",
        "orders",
        ["order_row_id"],
        ["row_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_order_documents_order_row_id_orders",
        "order_documents",
        "orders",
        ["order_row_id"],
        ["row_id"],
        ondelete="CASCADE",
    )

    op.alter_column("order_items", "order_row_id", nullable=False)
    op.alter_column("order_history", "order_row_id", nullable=False)
    op.alter_column("order_documents", "order_row_id", nullable=False)

    # Remove old order_id columns from children.
    op.drop_column("order_items", "order_id")
    op.drop_column("order_history", "order_id")
    op.drop_column("order_documents", "order_id")

    # 3) Orders: switch PK to row_id, keep stable business id and add (id, version) uniqueness.
    # CASCADE drops FKs that depend on orders_pkey (e.g. deal_document_forms_deal_id_fkey)
    op.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_pkey CASCADE")
    op.create_primary_key("orders_pkey", "orders", ["row_id"])
    op.create_unique_constraint("uq_orders_id_version", "orders", ["id", "version"])
    op.create_index("ix_orders_row_id", "orders", ["row_id"], unique=False)
    op.execute("ALTER TABLE orders ALTER COLUMN version DROP DEFAULT")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate order_id columns in children (legacy shape).
    op.add_column("order_items", sa.Column("order_id", sa.Integer(), nullable=True))
    op.add_column("order_history", sa.Column("order_id", sa.Integer(), nullable=True))
    op.add_column("order_documents", sa.Column("order_id", sa.Integer(), nullable=True))

    # Backfill old order_id from orders.row_id mapping.
    op.execute(
        """
        UPDATE order_items oi
        SET order_id = o.id
        FROM orders o
        WHERE oi.order_row_id = o.row_id
        """
    )
    op.execute(
        """
        UPDATE order_history oh
        SET order_id = o.id
        FROM orders o
        WHERE oh.order_row_id = o.row_id
        """
    )
    op.execute(
        """
        UPDATE order_documents od
        SET order_id = o.id
        FROM orders o
        WHERE od.order_row_id = o.row_id
        """
    )

    op.execute(
        "ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_order_row_id_orders"
    )
    op.execute(
        "ALTER TABLE order_history DROP CONSTRAINT IF EXISTS fk_order_history_order_row_id_orders"
    )
    op.execute(
        "ALTER TABLE order_documents DROP CONSTRAINT IF EXISTS fk_order_documents_order_row_id_orders"
    )

    op.create_foreign_key(
        "order_items_order_id_fkey",
        "order_items",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "order_history_order_id_fkey",
        "order_history",
        "orders",
        ["order_id"],
        ["id"],
    )
    op.create_foreign_key(
        "order_documents_order_id_fkey",
        "order_documents",
        "orders",
        ["order_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column("order_items", "order_id", nullable=False)
    op.alter_column("order_history", "order_id", nullable=False)
    op.alter_column("order_documents", "order_id", nullable=False)

    op.drop_column("order_items", "order_row_id")
    op.drop_column("order_history", "order_row_id")
    op.drop_column("order_documents", "order_row_id")

    # Restore old orders PK shape.
    op.drop_index("ix_orders_row_id", table_name="orders")
    op.drop_constraint("uq_orders_row_id", "orders", type_="unique")
    op.drop_constraint("uq_orders_id_version", "orders", type_="unique")
    op.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_pkey")
    op.create_primary_key("orders_pkey", "orders", ["id"])
    op.drop_column("orders", "version")
    op.drop_column("orders", "row_id")
    op.execute("DROP SEQUENCE IF EXISTS orders_row_id_seq")
