"""
Пересобирает bill*.docx и supply_contract.docx как минимальные шаблоны docxtpl.

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


def write_supply_contract(path: Path) -> None:
	doc = Document()
	doc.add_heading("ДОГОВОР ПОСТАВКИ № {{ supply_contract.number }}", level=0)
	_para(doc, "от {{ supply_contract_date_fmt }} г.")
	_para(
		doc,
		"{% if seller.company_type != 'ИП' %}"
		"{{ seller.company_name }}, далее «Поставщик», в лице {{ supply_contract.officials[0].position or '_____________' }} "
		"{% if supply_contract.officials[0].full_name %}{{ supply_contract.officials[0].full_name }}{% else %}_____________{% endif %}, "
		"{% if supply_contract.officials[0].is_base %}действующего на основании {{ supply_contract.officials[0].base_document }} "
		"{{ supply_contract.officials[0].base_document_name }}{% endif %}, с одной стороны, "
		"{% else %}"
		"{{ seller.company_name }}, далее «Поставщик», ОГРНИП {{ seller.ogrn }}, с одной стороны, "
		"{% endif %}",
	)
	_para(
		doc,
		"{% if buyer.company_type != 'ИП' %}"
		"{{ buyer.company_name }}, далее «Покупатель», с другой стороны, "
		"{% else %}"
		"{{ buyer.company_name }}, далее «Покупатель», ОГРНИП {{ buyer.ogrn }}, с другой стороны, "
		"{% endif %}"
		"заключили настоящий Договор поставки о нижеследующем:",
	)
	_para(doc, "{% if supply_contract.supply_contract_text %}{{ supply_contract.supply_contract_text }}{% endif %}")
	_para(
		doc,
		"{% if supply_contract.supplier_details_check %}"
		"Поставщик: {{ seller.company_name }}, ИНН {{ seller.inn }}, КПП {{ seller.kpp }}. "
		"Адрес: {{ seller.legal_address }}, тел. {{ seller.phone }}, email {{ seller.email }}. "
		"Банк: {{ seller.bank_name }}, БИК {{ seller.bic }}, р/с {{ seller.account_number }}. "
		"{% endif %}",
	)
	_para(
		doc,
		"{% if supply_contract.buyer_details_check %}"
		"Покупатель: {{ buyer.company_name }}, ИНН {{ buyer.inn }}, КПП {{ buyer.kpp }}. "
		"Адрес: {{ buyer.legal_address }}. "
		"{% endif %}",
	)
	_para(doc, "Спецификация № {{ supply_contract.specification_number }} от {{ specification_date_fmt }} г.")
	_para(
		doc,
		"{% for item in items %}"
		"{{ loop.index }}. {{ item.product_name }} — {{ item.quantity }} {{ item.unit_of_measurement }} × "
		"{{ item.price }} = {{ item.amount }}; "
		"{% endfor %}",
	)
	_para(doc, "Сумма без НДС: {{ total_amount_excl_vat }}, НДС: {{ amount_vat_rate }}, итого: {{ total_amount }}")
	_para(doc, "{% if supply_contract.specification_text %}{{ supply_contract.specification_text }}{% endif %}")
	_para(
		doc,
		"Поставщик: {{ seller.company_name }} / {% if supply_contract.officials[0].full_name %}"
		"{{ supply_contract.officials[0].full_name }}{% else %}_____________{% endif %} /",
	)
	path.parent.mkdir(parents=True, exist_ok=True)
	doc.save(str(path))
	print("Wrote", path)


def main() -> None:
	root = Path(__file__).resolve().parents[1]
	docx_dir = root / "app" / "templates" / "docx"
	write_bill_variant(docx_dir / "bill.docx", "Счёт")
	write_bill_variant(docx_dir / "bill_contract.docx", "Счёт (договор)")
	write_bill_variant(docx_dir / "bill_offer.docx", "Счёт (оферта)")
	write_supply_contract(docx_dir / "supply_contract.docx")


if __name__ == "__main__":
	main()
