"""Контекст Jinja2/docxtpl из DealResponse для подстановки в шаблоны .docx."""
from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any

from app.api.purchases.company_party_line import format_company_party_line, strip_leading_org_type
from app.api.purchases.docx_plain_text import sanitize_supply_contract_docx_fields
from app.api.purchases.schemas import DealResponse


def _docx_non_breaking_name(value: str | None) -> str:
	"""ФИО в docx/pdf: неразрывные пробелы, чтобы LibreOffice не рвал строку посередине."""
	text = (value or "").strip()
	if not text:
		return ""
	return "\u00a0".join(text.split())


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


def _nulls_to_empty(value: Any) -> Any:
	"""
	В docxtpl/Jinja `{{ None }}` печатается как «None».
	Перед рендером все None → '' (пробел/пусто), без строк «None».
	"""
	if value is None:
		return ""
	if isinstance(value, dict):
		return {k: _nulls_to_empty(v) for k, v in value.items()}
	if isinstance(value, list):
		return [_nulls_to_empty(v) for v in value]
	if isinstance(value, tuple):
		return tuple(_nulls_to_empty(v) for v in value)
	return value


_EMPTY_SUPPLY_CONTRACT_OFFICIAL: dict[str, Any] = {
	"full_name": "",
	"position": "",
	"is_base": False,
	"base_document": "",
	"base_document_name": "",
}


def _ensure_supply_contract_defaults(data: dict[str, Any]) -> None:
	"""Заглушки для supply_contract.docx — безопасный доступ к officials[0]."""
	supply_contract = data.get("supply_contract")
	if not isinstance(supply_contract, dict):
		return

	officials = supply_contract.get("officials")
	if not isinstance(officials, list) or len(officials) == 0:
		supply_contract["officials"] = [_EMPTY_SUPPLY_CONTRACT_OFFICIAL.copy()]


def _enrich_bill_payment_docx(data: dict[str, Any]) -> None:
	"""Поля для bill.docx: срок оплаты, НДС, строки поставщика/покупателя."""
	bill = data.get("bill")
	if not isinstance(bill, dict):
		return

	payment_days = (bill.get("payment_terms") or "").strip()
	if payment_days:
		bill["payment_validity_text"] = (
			f"Счет действителен в течении {payment_days} рабочих дней с момента выставления"
		)
	else:
		bill["payment_validity_text"] = ""

	show_vat = bool(data.get("amount_with_vat_rate"))
	bill["show_vat_row"] = show_vat
	bill["vat_amount_display"] = data.get("amount_vat_rate", "") if show_vat else ""

	seller = data.get("seller_company") if isinstance(data.get("seller_company"), dict) else {}
	buyer = data.get("buyer_company") if isinstance(data.get("buyer_company"), dict) else {}

	data["seller_party_line"] = format_company_party_line(seller)
	data["buyer_party_line"] = format_company_party_line(buyer)
	data["bill_number"] = bill.get("number") or data.get("seller_order_number") or ""
	data["items_count"] = len(data.get("items") or [])


_PAYMENT_PLACEHOLDER_RE = re.compile(r"\{\{\s*СРОК_ОПЛАТЫ")
_DELIVERY_PLACEHOLDER_RE = re.compile(r"\{\{\s*СРОК_ПОСТАВКИ")
_ANY_PLACEHOLDER_RE = re.compile(r"\{\{\s*[^}]+\s*\}\}")
_CONDITION_NUM_RE = re.compile(r"^(\s*)\d+([.)])")
_CONDITION_START_RE = re.compile(r"^\s*\d+[.)]")


def _ph(name: str) -> re.Pattern[str]:
	"""{{ ИМЯ }} с произвольными пробелами внутри скобок."""
	return re.compile(r"\{\{\s*" + re.escape(name) + r"\s*\}\}")


def _filter_terms_lines_for_docx(
	text: str,
	*,
	include_payment: bool,
	include_delivery: bool,
) -> str:
	"""Как на фронте: скрыть строки с плейсхолдерами сроков и перенумеровать пункты."""
	lines = text.split("\n")
	filtered: list[str] = []
	for line in lines:
		if not line.strip():
			filtered.append(line)
			continue
		if _PAYMENT_PLACEHOLDER_RE.search(line) and not include_payment:
			continue
		if _DELIVERY_PLACEHOLDER_RE.search(line) and not include_delivery:
			continue
		filtered.append(line)

	condition_no = 0
	renumbered: list[str] = []
	for line in filtered:
		if not _CONDITION_START_RE.match(line):
			renumbered.append(line)
			continue
		condition_no += 1
		renumbered.append(_CONDITION_NUM_RE.sub(rf"\g<1>{condition_no}\2", line, count=1))
	return "\n".join(renumbered)


def _substitute_bill_term_placeholders(text: str, data: dict[str, Any]) -> str:
	"""
	Подставить поля условий. Нет значения → пустая строка.
	Служебные {{ … }} в готовый DOC/PDF не попадают никогда.
	"""
	if not text:
		return ""
	bill = data.get("bill") if isinstance(data.get("bill"), dict) else {}
	seller = data.get("seller_company") if isinstance(data.get("seller_company"), dict) else {}
	doc_type = (bill.get("document_type") or "").strip()

	number = str(data.get("bill_number") or bill.get("number") or data.get("seller_order_number") or "")
	date_fmt = str(data.get("bill_date_fmt") or "")
	if doc_type in ("bill-offer", "bill_offer"):
		payment = str(bill.get("payment_terms_offer") or "")
	elif doc_type in ("bill-contract", "bill_contract"):
		payment = str(bill.get("payment_terms_contract") or "")
	else:
		payment = str(
			bill.get("payment_terms")
			or bill.get("payment_terms_contract")
			or bill.get("payment_terms_offer")
			or ""
		)
	delivery = str(bill.get("delivery_terms_contract") or "")
	production = (seller.get("production_address") or "").strip()
	company_name = str(seller.get("company_name") or "")

	replacements: list[tuple[re.Pattern[str], str]] = [
		(_ph("НОМЕР_СЧЕТА"), number),
		(_ph("ДАТА"), date_fmt),
		(_ph("СРОК_ОПЛАТЫ"), payment),
		(_ph("СРОК_ПОСТАВКИ"), delivery),
		(_ph("СРОК_ОПЛАТЫ_СЧЕТА_ДОГОВОРА"), str(bill.get("payment_terms_contract") or "")),
		(_ph("СРОК_ОПЛАТЫ_СЧЕТА_ОФЕРТЫ"), str(bill.get("payment_terms_offer") or "")),
		(_ph("СРОК_ПОСТАВКИ_СЧЕТА_ДОГОВОРА"), delivery),
		(_ph("НАЗВАНИЕ_КОМПАНИИ_ПОСТАВЩИКА"), company_name),
		(_ph("АДРЕС_ПРОИЗВОДСТВА_ПОСТАВЩИКА"), production),
	]
	out = text
	for pattern, value in replacements:
		out = pattern.sub(value, out)
	# Любой оставшийся {{ ЧТО_УГОДНО }} — стереть (пустая подстановка)
	return _ANY_PLACEHOLDER_RE.sub("", out)


def _enrich_bill_contract_offer_docx(data: dict[str, Any]) -> None:
	"""
	Поля для bill_contract.docx / bill_offer.docx:
	тип бланка, тексты условий, галки реквизитов (show_* для шаблонов).
	"""
	bill = data.get("bill")
	if not isinstance(bill, dict):
		bill = {}
		data["bill"] = bill

	# Уже приходят из model_dump: document_type, contract_terms_text_*, *_details_check
	bill.setdefault("document_type", "bill")
	bill.setdefault("contract_terms_text_contract", "")
	bill.setdefault("contract_terms_text_offer", "")

	show_supplier = bool(bill.get("supplier_details_check", True))
	show_buyer = bool(bill.get("buyer_details_check", True))
	bill["supplier_details_check"] = show_supplier
	bill["buyer_details_check"] = show_buyer
	# Алиасы для шаблонов (как в supply_contract / UI-галках)
	bill["show_supplier_details"] = show_supplier
	bill["show_buyer_details"] = show_buyer
	data["show_supplier_details"] = show_supplier
	data["show_buyer_details"] = show_buyer

	doc_type = (bill.get("document_type") or "bill").strip()
	if doc_type in ("bill-contract", "bill_contract"):
		terms = bill.get("contract_terms_text_contract") or ""
		bill["bill_title"] = "Счет-договор"
		include_payment = bool(str(bill.get("payment_terms_contract") or "").strip())
		include_delivery = bool(str(bill.get("delivery_terms_contract") or "").strip())
	elif doc_type in ("bill-offer", "bill_offer"):
		terms = bill.get("contract_terms_text_offer") or ""
		bill["bill_title"] = "Счет-оферта"
		include_payment = bool(str(bill.get("payment_terms_offer") or "").strip())
		include_delivery = True
	else:
		terms = ""
		bill["bill_title"] = "Счет на оплату"
		include_payment = True
		include_delivery = True

	terms = _filter_terms_lines_for_docx(
		terms,
		include_payment=include_payment,
		include_delivery=include_delivery,
	)
	terms = _substitute_bill_term_placeholders(terms, data)
	bill["contract_terms_text"] = terms
	data["contract_terms_text"] = terms
	data["bill_title"] = bill["bill_title"]

	# Оферта: доп. информация — только offer-поле (не текст счёта на оплату)
	extra = str(bill.get("additional_info_offer") or "")
	bill["additional_info_offer"] = _substitute_bill_term_placeholders(extra, data) if extra else ""

	if not data.get("bill_number"):
		data["bill_number"] = bill.get("number") or data.get("seller_order_number") or ""
	if "items_count" not in data:
		data["items_count"] = len(data.get("items") or [])
	if "seller_party_line" not in data or "buyer_party_line" not in data:
		seller = data.get("seller_company") if isinstance(data.get("seller_company"), dict) else {}
		buyer = data.get("buyer_company") if isinstance(data.get("buyer_company"), dict) else {}
		data.setdefault("seller_party_line", format_company_party_line(seller))
		data.setdefault("buyer_party_line", format_company_party_line(buyer))
	# НДС-флаги нужны и contract/offer (общая таблица итогов)
	if "show_vat_row" not in bill:
		show_vat = bool(data.get("amount_with_vat_rate"))
		bill["show_vat_row"] = show_vat
		bill["vat_amount_display"] = data.get("amount_vat_rate", "") if show_vat else ""
	bill.setdefault("officials", [])
	bill.setdefault("reason", "")


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


def _ensure_order_docx_signatures(data: dict[str, Any]) -> None:
	"""
	Шаблон order.docx (legacy): блок «Менеджер» читает bill.officials[0].full_name.
	Для заказа без счёта подставляем ФИО продавца из seller_company.owner_name.
	"""
	seller_company = data.get("seller_company") if isinstance(data.get("seller_company"), dict) else {}
	seller_block = data.get("seller") if isinstance(data.get("seller"), dict) else {}
	seller_name = seller_company.get("owner_name") or seller_block.get("full_name") or ""
	data["seller_manager_name"] = seller_name

	bill = data.get("bill")
	if not isinstance(bill, dict):
		bill = {}
		data["bill"] = bill
	officials = bill.get("officials")
	if not isinstance(officials, list) or len(officials) == 0:
		bill["officials"] = [{"id": 0, "full_name": seller_name, "position": ""}]
		return
	first = officials[0]
	if isinstance(first, dict) and not first.get("full_name"):
		first["full_name"] = seller_name


def _enrich_supply_contract_docx(data: dict[str, Any]) -> None:
	"""Договор поставки: должностное лицо, номер спецификации, реквизиты для docx."""
	supply_contract = data.get("supply_contract")
	if not isinstance(supply_contract, dict):
		supply_contract = {}
		data["supply_contract"] = supply_contract

	officials = supply_contract.get("officials")
	if not isinstance(officials, list):
		officials = []

	seller_company = data.get("seller_company") if isinstance(data.get("seller_company"), dict) else {}
	owner_name = (seller_company.get("owner_name") or "").strip()

	if not officials:
		if owner_name:
			officials = [
				{
					"id": 0,
					"full_name": owner_name,
					"position": "Генеральный директор",
					"is_base": False,
					"base_document": "",
					"base_document_name": "",
				}
			]
			supply_contract["officials"] = officials
	elif isinstance(officials[0], dict) and not (officials[0].get("full_name") or "").strip():
		if owner_name:
			officials[0]["full_name"] = owner_name
			officials[0].setdefault("position", "Генеральный директор")

	if not (supply_contract.get("specification_number") or "").strip():
		supply_contract["specification_number"] = "1"

	if not data.get("specification_date_fmt"):
		data["specification_date_fmt"] = data.get("supply_contract_date_fmt") or ""

	if not supply_contract.get("supplier_details_check"):
		supply_contract["supplier_details_check"] = bool(seller_company.get("inn"))
	buyer_company = data.get("buyer_company") if isinstance(data.get("buyer_company"), dict) else {}
	if not supply_contract.get("buyer_details_check"):
		supply_contract["buyer_details_check"] = bool(buyer_company.get("inn"))

	for party_key in ("seller", "buyer"):
		party = data.get(party_key)
		if not isinstance(party, dict):
			continue
		company_name = party.get("company_name") or ""
		company_type = party.get("company_type") or ""
		if company_name:
			short_name = strip_leading_org_type(company_name, company_type or None)
			party["company_name"] = (
				f"{company_type} {short_name}".strip() if company_type else short_name
			)

	if officials and isinstance(officials[0], dict) and officials[0].get("full_name"):
		officials[0]["full_name"] = _docx_non_breaking_name(str(officials[0]["full_name"]))

	for party_key in ("seller", "buyer"):
		party = data.get(party_key)
		if isinstance(party, dict) and party.get("full_name"):
			party["full_name"] = _docx_non_breaking_name(str(party["full_name"]))


def build_deal_docx_context(deal: DealResponse) -> dict[str, Any]:
	"""
	Словарь для docxtpl: вложенная структура как в API (by_alias), плюс даты в формате ДД.ММ.ГГГГ.
	Суммы `total_amount`, `total_amount_excl_vat`, `amount_vat_rate`, поля `price` / `quantity` / `amount` в `items` — строки вида 100,000.00.
	В шаблоне: {{ id }}, {{ buyer_company.company_name }}, {% for item in items %} ...
	"""
	data: dict[str, Any] = deal.model_dump(mode="json", by_alias=True)
	_apply_docx_money_formatting(data)
	data["contract_date_fmt"] = _fmt_date(deal.contract_date)
	# Если bill_date не проставлен, но номер счёта есть — дата заказа/создания лучше пустого «от  г.»
	data["bill_date_fmt"] = (
		_fmt_date(deal.bill_date)
		or _fmt_date(deal.created_at)
	)
	data["supply_contracts_date_fmt"] = _fmt_date(deal.supply_contract_date)
	data["supply_contract_date_fmt"] = _fmt_date(deal.supply_contract_date)
	if deal.supply_contract and deal.supply_contract.specification_date:
		data["specification_date_fmt"] = _fmt_date(deal.supply_contract.specification_date)
	data["created_at_fmt"] = _fmt_date(deal.created_at)
	data["updated_at_fmt"] = _fmt_date(deal.updated_at)
	# Старые шаблоны / клиентский docx использовали `total` вместо `total_amount`
	data["total"] = data.get("total_amount")
	data["total_word"] = data.get("total_amount_word") or ""

	# Алиасы для шаблонов с короткими именами seller / buyer
	seller_company = data.get("seller_company") if isinstance(data.get("seller_company"), dict) else {}
	buyer_company = data.get("buyer_company") if isinstance(data.get("buyer_company"), dict) else {}
	data["seller"] = {
		**seller_company,
		"full_name": seller_company.get("owner_name") or "",
	}
	data["buyer"] = {
		**buyer_company,
		"full_name": buyer_company.get("owner_name") or "",
	}

	_ensure_supply_contract_defaults(data)
	_enrich_supply_contract_docx(data)
	_ensure_order_docx_signatures(data)
	_enrich_bill_payment_docx(data)
	_enrich_bill_contract_offer_docx(data)
	sanitize_supply_contract_docx_fields(data)
	if "specification_date_fmt" not in data:
		data["specification_date_fmt"] = ""

	# Последний шаг: ни одно «None» не должно попасть в DOC/PDF
	return _nulls_to_empty(data)
