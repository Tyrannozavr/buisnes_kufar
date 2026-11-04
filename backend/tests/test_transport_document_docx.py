"""Unit-тесты сборки DOCX бланков перевозки из payload_json."""

from datetime import datetime
from io import BytesIO

from docx import Document

from app.api.purchases.services.transport_document_docx import (
	DOC_TITLES,
	build_transport_document_docx_bytes,
	format_doc_date,
)


def test_format_doc_date_style2():
	assert format_doc_date(datetime(2026, 11, 4), style2=True) == "«04» ноября 2026"
	assert format_doc_date(None, style2=True).startswith("«____»")


def test_build_carriage_contract_docx_contains_payload_fields():
	raw = build_transport_document_docx_bytes(
		doc_type="carriage_contract",
		number="999",
		date=datetime(2025, 4, 8),
		payload_json={
			"city": "Москва",
			"bodyHtml": "<p><strong>1. Предмет</strong></p><p>Текст договора</p>",
			"customer": {
				"fullName": "ООО Заказчик Тест",
				"companyType": "ООО",
				"officialPosition": "Директор",
				"officialName": "Иванов И.И.",
				"foundationKind": "Устава",
				"inn": "7700000001",
			},
			"carrier": {
				"fullName": "ООО Перевозчик Тест",
				"companyType": "ООО",
				"officialPosition": "Директор",
				"officialName": "Петров П.П.",
				"foundationKind": "Устава",
				"inn": "7700000002",
			},
			"customerDetailsCheck": True,
			"carrierDetailsCheck": True,
		},
	)
	assert raw[:2] == b"PK"
	doc = Document(BytesIO(raw))
	text = "\n".join(p.text for p in doc.paragraphs)
	assert DOC_TITLES["carriage_contract"] in text
	assert "999" in text
	assert "ООО Заказчик Тест" in text
	assert "Текст договора" in text
	assert "<p>" not in text


def test_build_strict_forwarder_assignment_docx():
	raw = build_transport_document_docx_bytes(
		doc_type="forwarder_assignment",
		number="1",
		date=datetime(2025, 5, 16),
		payload_json={
			"shipper": {"fullName": "Грузоотправитель А", "inn": "1"},
			"client": {"fullName": "Клиент Б", "inn": "2"},
			"consignee": {"fullName": "Получатель В", "inn": "3"},
			"forwarder": {"fullName": "Экспедитор Г", "inn": "4"},
			"destination": "Санкт-Петербург",
			"signatureName": "Сидоров",
			"signaturePosition": "Менеджер",
		},
		parent_number="00001",
		parent_date=datetime(2025, 5, 1),
	)
	assert raw[:2] == b"PK"
	doc = Document(BytesIO(raw))
	text = "\n".join(p.text for p in doc.paragraphs)
	assert "ПОРУЧЕНИЕ ЭКСПЕДИТОРУ" in text
	assert "00001" in text
	table_text = "\n".join(
		cell.text for table in doc.tables for row in table.rows for cell in row.cells
	)
	assert "Санкт-Петербург" in table_text
	assert "Грузоотправитель А" in table_text
