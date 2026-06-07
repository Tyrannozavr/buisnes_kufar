from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from app.api.purchases.services.docx_template_service import (
	SUPPLY_CONTRACT_DOCX_FILENAME,
	render_docx_bytes,
	resolve_docx_template_path,
)

ctx = {
	"supply_contract": {
		"number": "00001",
		"specification_number": "1",
		"officials": [
			{
				"full_name": "Ivan",
				"position": "Dir",
				"is_base": False,
				"base_document": "",
				"base_document_name": "",
			}
		],
		"supply_contract_text": "Some text with & ampersand",
		"specification_text": "",
		"supplier_details_check": True,
		"buyer_details_check": True,
	},
	"seller_company": {
		"company_name": "Логистика 'Бета'",
		"company_type": "ООО",
		"city": "Москва",
		"inn": "7701234567",
		"kpp": "770101001",
		"ogrn": "1027700132195",
		"legal_address": "ул. Тест",
		"index": "",
		"account_number": "",
		"correspondent_bank_account": "",
		"product_address": "",
		"bic": "",
		"phone": "",
		"email": "",
	},
	"buyer_company": {
		"company_name": "Логистика 'Альфа'",
		"inn": "",
		"kpp": "",
		"ogrn": "",
		"legal_address": "",
		"index": "",
		"account_number": "",
		"correspondent_bank_account": "",
		"product_address": "",
		"bic": "",
		"phone": "",
		"email": "",
	},
	"buyer": {"company_name": "Логистика 'Альфа'", "company_type": "ООО", "ogrn": ""},
	"seller": {"company_name": "Логистика 'Бета'", "company_type": "ООО", "ogrn": ""},
	"items": [
		{
			"product_name": "Товар",
			"quantity": "1.00",
			"unit_of_measurement": "шт",
			"price": "100.00",
			"amount": "100.00",
		}
	],
	"supply_contract_date_fmt": "01.01.2025",
	"specification_date_fmt": "",
	"total_amount_excl_vat": "100.00",
	"amount_vat_rate": "20.00",
	"total_amount": "120.00",
}

path = resolve_docx_template_path(SUPPLY_CONTRACT_DOCX_FILENAME)
data = render_docx_bytes(path, ctx)
out = Path(__file__).resolve().parent / "tmp_realistic.docx"
out.write_bytes(data)

with zipfile.ZipFile(out) as z:
	print("zip test:", z.testzip())
	xml = z.read("word/document.xml").decode("utf-8")
	bad = re.findall(r"<w:t[^>]*>[^<]*[&<>][^<]*</w:t>", xml)
	print("unescaped in w:t:", len(bad), bad[:3])
	print("colors:", sorted(set(re.findall(r'w:color w:val="([^"]+)"', xml))))
	print("rStyles:", sorted(set(re.findall(r'w:rStyle w:val="([^"]+)"', xml))))
	left = re.findall(r"\{\{[^}]+\}\}|\{%[^%]+%\}", xml)
	print("leftover jinja:", len(left), left[:5])
	try:
		ET.fromstring(xml)
		print("xml parse: OK")
	except ET.ParseError as exc:
		print("xml parse: FAIL", exc)

from docx import Document

Document(str(out))
print("python-docx open: OK")
print("written:", out)
