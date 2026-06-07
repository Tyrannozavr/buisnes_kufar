"""Тесты очистки HTML перед рендером docx (без БД)."""
from __future__ import annotations

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
