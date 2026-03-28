"""Сумма сделки прописью на русском (рубли и копейки)."""
from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from num2words import num2words


def format_total_amount_word(amount: float | None) -> str:
	"""
	Преобразует итоговую сумму сделки в строку для печати (num2words, RUB).
	Округление до 2 знаков — как у денежных сумм.
	"""
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
