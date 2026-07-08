"""add company_contract table (ЛК Договоры)

Revision ID: f3a8c1d2e4b5
Revises: e5a2b3c4d6f7
Create Date: 2026-07-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3a8c1d2e4b5"
down_revision: Union[str, None] = "e5a2b3c4d6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"company_contract",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("seller_company_id", sa.Integer(), nullable=False),
		sa.Column("buyer_company_id", sa.Integer(), nullable=False),
		sa.Column("number", sa.String(length=20), nullable=False),
		sa.Column("date", sa.DateTime(), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=True),
		sa.Column("updated_at", sa.DateTime(), nullable=True),
		sa.ForeignKeyConstraint(["buyer_company_id"], ["companies.id"], ondelete="CASCADE"),
		sa.ForeignKeyConstraint(["seller_company_id"], ["companies.id"], ondelete="CASCADE"),
		sa.PrimaryKeyConstraint("id"),
		sa.UniqueConstraint(
			"seller_company_id",
			"buyer_company_id",
			"number",
			name="uq_company_contract_seller_buyer_number",
		),
	)
	op.create_index(
		op.f("ix_company_contract_buyer_company_id"),
		"company_contract",
		["buyer_company_id"],
		unique=False,
	)
	op.create_index(
		op.f("ix_company_contract_seller_company_id"),
		"company_contract",
		["seller_company_id"],
		unique=False,
	)


def downgrade() -> None:
	op.drop_index(op.f("ix_company_contract_seller_company_id"), table_name="company_contract")
	op.drop_index(op.f("ix_company_contract_buyer_company_id"), table_name="company_contract")
	op.drop_table("company_contract")
