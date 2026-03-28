"""Контекст Jinja2/docxtpl из DealResponse для подстановки в шаблоны .docx."""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from app.api.purchases.schemas import DealResponse


def _fmt_date(value: datetime | None) -> str:
	if value is None:
		return ""
	return value.strftime("%d.%m.%Y")


def _fmt_money_us(value: Any) -> str:
	"""Строка для печати: разделитель тысяч запятая, два знака после точки (например 100,000.00)."""
	if value is None:
		return ""
	try:
		n = float(value)
	except (TypeError, ValueError):
		return str(value)
	if math.isnan(n):
		return ""
	return f"{n:,.2f}"


def _apply_docx_money_formatting(data: dict[str, Any]) -> None:
	"""Подменяет числовые суммы на отформатированные строки только для рендера docx."""
	for key in ("total_amount", "total_amount_excl_vat", "amount_vat_rate"):
		if key in data:
			data[key] = _fmt_money_us(data[key])
	items = data.get("items")
	if not isinstance(items, list):
		return
	for row in items:
		if not isinstance(row, dict):
			continue
		for col in ("price", "quantity", "amount"):
			if col in row:
				row[col] = _fmt_money_us(row[col])


def build_deal_docx_context(deal: DealResponse) -> dict[str, Any]:
	"""
	Словарь для docxtpl: вложенная структура как в API (by_alias), плюс даты в формате ДД.ММ.ГГГГ.
	Суммы `total_amount`, `total_amount_excl_vat`, `amount_vat_rate`, поля `price` / `quantity` / `amount` в `items` — строки вида 100,000.00.
	В шаблоне: {{ id }}, {{ buyer_company.company_name }}, {% for item in items %} ...
	"""
	data: dict[str, Any] = deal.model_dump(mode="json", by_alias=True)
	_apply_docx_money_formatting(data)
	data["contract_date_fmt"] = _fmt_date(deal.contract_date)
	data["bill_date_fmt"] = _fmt_date(deal.bill_date)
	data["supply_contracts_date_fmt"] = _fmt_date(deal.supply_contracts_date)
	data["created_at_fmt"] = _fmt_date(deal.created_at)
	data["updated_at_fmt"] = _fmt_date(deal.updated_at)
	# Старые шаблоны / клиентский docx использовали `total` вместо `total_amount`
	data["total"] = data.get("total_amount")
	data["total_word"] = data.get("total_amount_word") or ""
	return data
