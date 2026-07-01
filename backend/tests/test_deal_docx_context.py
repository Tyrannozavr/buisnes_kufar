"""Тесты очистки HTML перед рендером docx (без БД)."""
from __future__ import annotations

from app.api.purchases.deal_docx_context import _ensure_order_docx_signatures, _enrich_bill_payment_docx
from app.api.purchases.docx_plain_text import html_to_plain_text, sanitize_supply_contract_docx_fields


def test_html_to_plain_text_strips_tags_and_keeps_content() -> None:
	html = (
		'<p>аааа</p><p><span data-supply-contract-field="seller.companyName" '
		'data-supply-contract-label="Название">Логистика \'Бета\'</span></p>'
	)
	result = html_to_plain_text(html)
	assert "<" not in result
	assert "Логистика 'Бета'" in result
	assert "аааа" in result


def test_html_to_plain_text_plain_string_unchanged() -> None:
	assert html_to_plain_text("простой текст") == "простой текст"


def test_sanitize_supply_contract_docx_fields() -> None:
	data = {
		"supply_contract": {
			"supply_contract_text": "<p>Условие 1</p><p>Условие 2</p>",
			"specification_text": "<p>Спец</p>",
		}
	}
	sanitize_supply_contract_docx_fields(data)
	assert data["supply_contract"]["supply_contract_text"] == "Условие 1\nУсловие 2"
	assert data["supply_contract"]["specification_text"] == "Спец"


def test_order_docx_manager_falls_back_to_seller_owner_name() -> None:
	"""order.docx (legacy): менеджер через bill.officials[0] — подставляем owner_name продавца."""
	data = {
		"seller_company": {"owner_name": "Дмитрий Тестов Сергеевич"},
		"seller": {"full_name": "Дмитрий Тестов Сергеевич"},
		"bill": None,
	}
	_ensure_order_docx_signatures(data)
	assert data["seller_manager_name"] == "Дмитрий Тестов Сергеевич"
	assert data["bill"]["officials"][0]["full_name"] == "Дмитрий Тестов Сергеевич"


def test_enrich_bill_payment_docx_payment_validity_and_vat() -> None:
	data = {
		"amount_with_vat_rate": True,
		"amount_vat_rate": "49.38",
		"seller_company": {
			"company_type": "ООО",
			"company_name": "ООО Поставщик Тест",
			"inn": "123",
			"kpp": "456",
			"index": "101000",
			"legal_address": "101000, г. Москва",
		},
		"buyer_company": {"company_name": "Покупатель"},
		"items": [{"product_name": "Товар"}],
		"bill": {"number": "00001", "payment_terms": "5", "reason": "Заказ №1"},
	}
	_enrich_bill_payment_docx(data)
	assert "5 рабочих дней" in data["bill"]["payment_validity_text"]
	assert data["bill"]["show_vat_row"] is True
	assert data["seller_party_line"].startswith("ООО Поставщик")
	assert data["items_count"] == 1
