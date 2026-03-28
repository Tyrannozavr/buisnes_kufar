"""
Пересобирает bill.docx / bill_contract.docx / bill_offer.docx как минимальные шаблоны docxtpl.

Старые файлы из Word часто ломают Jinja (плейсхолдеры разбиты на несколько w:r).
Запуск из корня backend: python scripts/build_minimal_deal_docx_templates.py
"""
from __future__ import annotations

from pathlib import Path

from docx import Document


def _para(doc: Document, text: str) -> None:
	p = doc.add_paragraph()
	p.add_run(text)


def write_bill_variant(path: Path, title: str) -> None:
	doc = Document()
	doc.add_heading(title, level=0)
	_para(
		doc,
		"Покупатель: {{ buyer_company.company_name }}, ИНН {{ buyer_company.inn }}, "
		"{{ buyer_company.legal_address }}",
	)
	_para(
		doc,
		"Продавец: {{ seller_company.company_name }}, ИНН {{ seller_company.inn }}, "
		"{{ seller_company.legal_address }}",
	)
	_para(
		doc,
		"{% if bill %}Счёт № {{ bill.number }}{% else %}Счёт (не заполнен){% endif %} от {{ bill_date_fmt }}",
	)
	_para(doc, "Позиции:")
	_para(
		doc,
		"{% for item in items %}"
		"{{ loop.index }}. {{ item.product_name }} — {{ item.quantity }} {{ item.unit_of_measurement }} × "
		"{{ item.price }} = {{ item.amount }}; "
		"{% endfor %}",
	)
	_para(doc, "НДС: {{ amount_vat_rate }}, итого: {{ total_amount }}")
	_para(doc, "{% if bill %}{{ bill.additional_info }}{% endif %}")
	path.parent.mkdir(parents=True, exist_ok=True)
	doc.save(str(path))
	print("Wrote", path)


def main() -> None:
	root = Path(__file__).resolve().parents[1]
	docx_dir = root / "app" / "templates" / "docx"
	write_bill_variant(docx_dir / "bill.docx", "Счёт")
	write_bill_variant(docx_dir / "bill_contract.docx", "Счёт (договор)")
	write_bill_variant(docx_dir / "bill_offer.docx", "Счёт (оферта)")


if __name__ == "__main__":
	main()
