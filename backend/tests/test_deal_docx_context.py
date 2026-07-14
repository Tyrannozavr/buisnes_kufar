"""Тесты очистки HTML перед рендером docx (без БД)."""
from __future__ import annotations

from app.api.purchases.deal_docx_context import (
	_enrich_supply_contract_docx,
	_ensure_order_docx_signatures,
	_enrich_bill_payment_docx,
	_enrich_bill_contract_offer_docx,
	_nulls_to_empty,
)
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


def test_nulls_to_empty_for_docx() -> None:
	"""Пустые реквизиты не должны попадать в DOC как строка «None»."""
	data = {
		"buyer_company": {
			"company_name": "ООО Покупатель",
			"account_number": None,
			"correspondent_bank_account": None,
			"bank_name": None,
			"bic": None,
		},
		"bill": {"officials": [{"position": None, "full_name": "Иванов"}]},
	}
	clean = _nulls_to_empty(data)
	assert clean["buyer_company"]["account_number"] == ""
	assert clean["buyer_company"]["bank_name"] == ""
	assert clean["bill"]["officials"][0]["position"] == ""
	assert clean["bill"]["officials"][0]["full_name"] == "Иванов"
	assert "None" not in str(clean)


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


def test_enrich_supply_contract_docx_fills_officials_and_spec_defaults() -> None:
	data = {
		"seller_company": {"owner_name": "Сергей Поставщик", "inn": "7707083893"},
		"buyer_company": {"inn": "7707083895"},
		"seller": {"company_name": "ООО Поставщик Тест", "company_type": "ООО"},
		"buyer": {"company_name": "ООО Покупатель", "company_type": "ООО"},
		"supply_contract": {"officials": [], "specification_number": ""},
		"supply_contract_date_fmt": "12.07.2026",
	}
	_enrich_supply_contract_docx(data)
	assert data["supply_contract"]["officials"][0]["full_name"] == "Сергей\u00a0Поставщик"
	assert data["supply_contract"]["specification_number"] == "1"
	assert data["specification_date_fmt"] == "12.07.2026"
	assert data["supply_contract"]["supplier_details_check"] is True
	assert data["seller"]["company_name"] == "ООО Поставщик Тест"


def test_enrich_bill_contract_offer_docx_terms_and_details_flags() -> None:
	data = {
		"bill_number": "00001",
		"bill_date_fmt": "14.07.2026",
		"seller_company": {"production_address": "ул. Складская, 2", "company_name": "ООО Поставщик"},
		"bill": {
			"document_type": "bill-contract",
			"contract_terms_text_contract": (
				"Договор № {{ НОМЕР_СЧЕТА }} от {{ ДАТА }} г.\n"
				"3.\tСрок {{ СРОК_ОПЛАТЫ }} дней\n"
				"4.\tПоставка {{ СРОК_ПОСТАВКИ }} дней"
			),
			"contract_terms_text_offer": "Оферта {{ НОМЕР_СЧЕТА }}",
			"payment_terms_contract": "9",
			"delivery_terms_contract": "10",
			"supplier_details_check": False,
			"buyer_details_check": True,
		},
	}
	_enrich_bill_contract_offer_docx(data)
	terms = data["bill"]["contract_terms_text"]
	assert "00001" in terms
	assert "14.07.2026" in terms
	assert "9" in terms
	assert "10" in terms
	assert "{{" not in terms
	assert data["show_supplier_details"] is False
	assert data["show_buyer_details"] is True

	data["bill"]["document_type"] = "bill-offer"
	data["bill"]["payment_terms_offer"] = "3"
	_enrich_bill_contract_offer_docx(data)
	assert data["bill"]["contract_terms_text"] == "Оферта 00001"
	assert "{{" not in data["bill"]["contract_terms_text"]


def test_enrich_bill_no_raw_placeholders_when_values_empty() -> None:
	"""Нет данных → пусто, но без служебных {{ ПОЛЕ }} в тексте."""
	data = {
		"bill_number": "",
		"bill_date_fmt": "",
		"seller_company": {"production_address": "", "company_name": ""},
		"bill": {
			"document_type": "bill-contract",
			"contract_terms_text_contract": (
				"Договор №{{НОМЕР_СЧЕТА}} от {{  ДАТА  }} г.\n"
				"Адрес: {{ АДРЕС_ПРОИЗВОДСТВА_ПОСТАВЩИКА }}\n"
				"Неизвестное: {{ ЧУЖОЕ_ПОЛЕ }}\n"
				"3.\tСрок {{ СРОК_ОПЛАТЫ }} дней"
			),
			"additional_info_offer": "Оферта {{ ДАТА }} / {{ XYZ }}",
			"payment_terms_contract": "",
			"delivery_terms_contract": "",
			"supplier_details_check": True,
			"buyer_details_check": True,
		},
	}
	_enrich_bill_contract_offer_docx(data)
	terms = data["bill"]["contract_terms_text"]
	assert "{{" not in terms
	assert "}}" not in terms
	assert "НОМЕР_СЧЕТА" not in terms
	assert "ЧУЖОЕ_ПОЛЕ" not in terms
	# строка со сроком оплаты скрыта (галка/значение пустое)
	assert "Срок" not in terms
	assert "Договор №" in terms
	assert "от" in terms and "г." in terms
