from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from app.api.purchases.deal_docx_context import build_deal_docx_context
from app.api.purchases.docx_plain_text import html_to_plain_text
from app.api.purchases.schemas import DealResponse, SupplyContractInDealResponse
from app.api.purchases.services.docx_template_service import (
	SUPPLY_CONTRACT_DOCX_FILENAME,
	render_docx_bytes,
	resolve_docx_template_path,
)

html = (
	'<p>аааа</p><p><span data-supply-contract-field="seller.companyName" '
	'data-supply-contract-label="Название организации (Поставщик)">Логистика \'Бетера\'</span></p>'
)

print("plain:", html_to_plain_text(html))

deal = DealResponse.model_validate(
	{
		"id": 1,
		"version": 1,
		"buyer_order_number": "1",
		"seller_order_number": "1",
		"buyer_company": {
			"company_id": 1,
			"company_name": "B",
			"company_type": "ООО",
			"name": "Иванов",
			"slug": "b",
			"phone": "",
			"email": "",
			"legal_address": "",
			"production_address": "",
		},
		"seller_company": {
			"company_id": 2,
			"company_name": "S",
			"company_type": "ООО",
			"name": "Петров",
			"slug": "s",
			"phone": "",
			"email": "",
			"legal_address": "",
			"production_address": "",
			"city": "M",
		},
		"items": [],
		"supply_contract": SupplyContractInDealResponse(
			number="1",
			supply_contract_text=html,
		).model_dump(by_alias=True),
	}
)
ctx = build_deal_docx_context(deal)
print("ctx text:", ctx["supply_contract"]["supply_contract_text"])

data = render_docx_bytes(resolve_docx_template_path(SUPPLY_CONTRACT_DOCX_FILENAME), ctx)
out = Path(__file__).resolve().parent / "tmp_with_html.docx"
out.write_bytes(data)

with zipfile.ZipFile(out) as z:
	xml = z.read("word/document.xml").decode("utf-8")
	print("contains <p>:", "<p>" in xml)
	print("contains &lt;p&gt;:", "&lt;p&gt;" in xml)
	print("zip test:", z.testzip())
	try:
		ET.fromstring(xml)
		print("xml: VALID")
	except ET.ParseError as exc:
		print("xml: INVALID", exc)
