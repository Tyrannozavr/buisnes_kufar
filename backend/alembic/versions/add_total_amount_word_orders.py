"""add total_amount_word to orders

Revision ID: add_total_amt_word
Revises: add_bill_offer_cols
Create Date: 2026-03-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_total_amt_word"
down_revision: Union[str, None] = "add_bill_offer_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	# Импорты только внутри upgrade: иначе Alembic грузит все модули миграций при старте.
	import math
	import warnings
	from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

	try:
		from num2words import num2words
	except ImportError:
		num2words = None  # type: ignore[assignment]
		warnings.warn(
			"num2words не найден: колонка total_amount_word добавлена, пропись для существующих "
			"строк не заполнена (пустая строка). Пересоберите backend-образ с num2words или "
			"выполните: pip install num2words && alembic downgrade -1 && alembic upgrade head",
			stacklevel=1,
		)

	def _format_total_amount_word(amount: float | None) -> str:
		if num2words is None:
			return ""
		if amount is None:
			return ""
		try:
			f = float(amount)
		except (TypeError, ValueError, OverflowError):
			return ""
		if math.isnan(f) or math.isinf(f):
			return ""
		try:
			d = Decimal(str(f)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
		except (InvalidOperation, ValueError, TypeError, OverflowError):
			return ""
		if d < 0:
			d = Decimal("0")
		try:
			return num2words(d, lang="ru", to="currency", currency="RUB")
		except Exception:
			return ""

	op.add_column(
		"orders",
		sa.Column("total_amount_word", sa.Text(), nullable=False, server_default=""),
	)
	if num2words is not None:
		conn = op.get_bind()
		rows = conn.execute(sa.text("SELECT row_id, total_amount FROM orders")).fetchall()
		for row in rows:
			rid, total = row[0], row[1]
			word = _format_total_amount_word(float(total) if total is not None else 0.0)
			conn.execute(
				sa.text("UPDATE orders SET total_amount_word = :w WHERE row_id = :rid"),
				{"w": word, "rid": rid},
			)
	op.alter_column("orders", "total_amount_word", server_default=None)


def downgrade() -> None:
	op.drop_column("orders", "total_amount_word")
