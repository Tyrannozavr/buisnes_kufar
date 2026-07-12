"""
Пересобирает bill*.docx и supply_contract.docx как минимальные шаблоны docxtpl.

Старые файлы из Word часто ломают Jinja (плейсхолдеры разбиты на несколько w:r).
Запуск из корня backend: python scripts/build_minimal_deal_docx_templates.py
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_BREAK, WD_LINE_SPACING, WD_PARAGRAPH_ALIGNMENT, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

CONTRACT_FONT_NAME = "Times New Roman"
CONTRACT_FONT_SIZE = Pt(12)
CONTRACT_RIGHT_COLUMN_TAB = Cm(9)


def _set_run_font(run, *, bold: bool = False) -> None:
	run.font.name = CONTRACT_FONT_NAME
	run.font.size = CONTRACT_FONT_SIZE
	run.bold = bold
	r_pr = run._element.get_or_add_rPr()
	r_fonts = OxmlElement("w:rFonts")
	r_fonts.set(qn("w:ascii"), CONTRACT_FONT_NAME)
	r_fonts.set(qn("w:hAnsi"), CONTRACT_FONT_NAME)
	r_fonts.set(qn("w:cs"), CONTRACT_FONT_NAME)
	r_fonts.set(qn("w:eastAsia"), CONTRACT_FONT_NAME)
	r_pr.insert(0, r_fonts)


def _apply_contract_document_style(doc: Document) -> None:
	normal = doc.styles["Normal"]
	normal.font.name = CONTRACT_FONT_NAME
	normal.font.size = CONTRACT_FONT_SIZE
	normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
	normal.paragraph_format.first_line_indent = Cm(1.25)

	for section in doc.sections:
		section.top_margin = Cm(2)
		section.bottom_margin = Cm(2)
		section.left_margin = Cm(2)
		section.right_margin = Cm(1)


def _para(doc: Document, text: str) -> None:
	p = doc.add_paragraph()
	run = p.add_run(text)
	_set_run_font(run)


def _contract_title(doc: Document, text: str) -> None:
	p = doc.add_paragraph()
	p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
	p.paragraph_format.first_line_indent = Cm(0)
	run = p.add_run(text)
	_set_run_font(run, bold=True)


def _contract_centered(doc: Document, text: str) -> None:
	p = doc.add_paragraph()
	p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
	p.paragraph_format.first_line_indent = Cm(0)
	run = p.add_run(text)
	_set_run_font(run)


def _contract_body_para(doc: Document, text: str) -> None:
	p = doc.add_paragraph()
	p.paragraph_format.first_line_indent = Cm(1.25)
	p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
	run = p.add_run(text)
	_set_run_font(run)


def _contract_page_break(doc: Document) -> None:
	p = doc.add_paragraph()
	p.paragraph_format.first_line_indent = Cm(0)
	run = p.add_run()
	run.add_break(WD_BREAK.PAGE)


def _set_paragraph_keep(paragraph, *, together: bool = True, with_next: bool = False) -> None:
	paragraph.paragraph_format.keep_together = together
	paragraph.paragraph_format.keep_with_next = with_next


def _add_two_column_lines(
	doc: Document,
	rows: list[tuple[str, str]],
	*,
	bold_header: bool = False,
	page_break_before: bool = False,
	keep_rows_together: bool = False,
) -> None:
	"""Две колонки без таблицы — табуляция, как в превью (без видимой сетки Word)."""
	if page_break_before:
		_contract_page_break(doc)

	last_row_idx = len(rows) - 1
	for row_idx, (left, right) in enumerate(rows):
		p = doc.add_paragraph()
		p.paragraph_format.first_line_indent = Cm(0)
		p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
		p.paragraph_format.tab_stops.add_tab_stop(CONTRACT_RIGHT_COLUMN_TAB, WD_TAB_ALIGNMENT.LEFT)
		keep_with_next = keep_rows_together and row_idx < last_row_idx
		_set_paragraph_keep(p, together=True, with_next=keep_with_next)

		is_header = bold_header and row_idx == 0
		left_run = p.add_run(left)
		_set_run_font(left_run, bold=is_header)
		p.add_run("\t")
		right_run = p.add_run(right)
		_set_run_font(right_run, bold=is_header)

	doc.add_paragraph()


def write_bill_payment(path: Path) -> None:
	doc = Document()
	doc.add_heading("Счет на оплату № {{ bill_number }} от {{ bill_date_fmt }} г.", level=0)
	_para(doc, "Банк: {{ seller_company.bank_name }}, БИК {{ seller_company.bic }}")
	_para(
		doc,
		"ИНН {{ seller_company.inn }}, КПП {{ seller_company.kpp }}, "
		"р/с {{ seller_company.account_number }}, к/с {{ seller_company.correspondent_bank_account }}",
	)
	_para(doc, "Получатель: {{ seller_company.company_type }} {{ seller_company.company_name }}")
	_para(doc, "Поставщик (исполнитель): {{ seller_party_line }}")
	_para(doc, "Покупатель (заказчик): {{ buyer_party_line }}")
	_para(doc, "{% if bill.reason %}Основание: {{ bill.reason }}{% endif %}")
	_para(
		doc,
		"{% for item in items %}"
		"{{ loop.index }}. {{ item.product_name }} — {{ item.quantity }} {{ item.unit_of_measurement }} × "
		"{{ item.price }} = {{ item.amount }}; "
		"{% endfor %}",
	)
	_para(doc, "Итого: {{ total_amount_excl_vat }}")
	_para(doc, "В том числе НДС: {% if bill.show_vat_row %}{{ bill.vat_amount_display }}{% endif %}")
	_para(doc, "Всего к оплате: {{ total_amount }}")
	_para(doc, "Всего наименований: {{ items_count }}, на сумму: {{ total_amount }} руб.")
	_para(doc, "{{ total_word }}")
	_para(doc, "{% if bill.payment_validity_text %}{{ bill.payment_validity_text }}{% endif %}")
	_para(doc, "{% if bill.additional_info %}{{ bill.additional_info }}{% endif %}")
	_para(
		doc,
		"{% for o in bill.officials %}{{ o.position }} {{ o.full_name }}{% if not loop.last %}; {% endif %}{% endfor %}",
	)
	path.parent.mkdir(parents=True, exist_ok=True)
	doc.save(str(path))
	print("Wrote", path)


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
	_apply_contract_document_style(doc)
	_contract_title(doc, "ДОГОВОР ПОСТАВКИ № {{ supply_contract.number }}")
	_contract_centered(doc, "от {{ supply_contract_date_fmt }} г.")
	_contract_body_para(
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
	_contract_body_para(
		doc,
		"{% if buyer.company_type != 'ИП' %}"
		"{{ buyer.company_name }}, далее «Покупатель», с другой стороны, "
		"{% else %}"
		"{{ buyer.company_name }}, далее «Покупатель», ОГРНИП {{ buyer.ogrn }}, с другой стороны, "
		"{% endif %}"
		"заключили настоящий Договор поставки о нижеследующем:",
	)
	_contract_body_para(
		doc,
		"{% if supply_contract.supply_contract_text %}{{ supply_contract.supply_contract_text }}{% endif %}",
	)
	_contract_body_para(doc, "Спецификация № {{ supply_contract.specification_number }} от {{ specification_date_fmt }} г.")
	_contract_body_para(
		doc,
		"{% for item in items %}"
		"{{ loop.index }}. {{ item.product_name }} — {{ item.quantity }} {{ item.unit_of_measurement }} × "
		"{{ item.price }} = {{ item.amount }}; "
		"{% endfor %}",
	)
	_contract_body_para(
		doc,
		"Сумма без НДС: {{ total_amount_excl_vat }}, НДС: {{ amount_vat_rate }}, итого: {{ total_amount }}",
	)
	_contract_body_para(
		doc,
		"{% if supply_contract.specification_text %}{{ supply_contract.specification_text }}{% endif %}",
	)
	_add_two_column_lines(
		doc,
		[
			(
				"{% if supply_contract.supplier_details_check %}ПОСТАВЩИК:{% endif %}",
				"{% if supply_contract.buyer_details_check %}ПОКУПАТЕЛЬ:{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}{{ seller.company_name }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}{{ buyer.company_name }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}{{ seller.index }}, {{ seller.legal_address }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}{{ buyer.index }}, {{ buyer.legal_address }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}ИНН {{ seller.inn }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}ИНН {{ buyer.inn }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}КПП {{ seller.kpp }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}КПП {{ buyer.kpp }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}Рас/счет № {{ seller.account_number or '' }} в {{ seller.bank_name or '' }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}Рас/счет № {{ buyer.account_number or '' }} в {{ buyer.bank_name or '' }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}{{ seller.correspondent_bank_account or '' }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}{{ buyer.correspondent_bank_account or '' }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}{{ seller.bic or '' }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}{{ buyer.bic or '' }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}{{ seller.email }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}{{ buyer.email }}{% endif %}",
			),
			(
				"{% if supply_contract.supplier_details_check %}{{ seller.phone }}{% endif %}",
				"{% if supply_contract.buyer_details_check %}{{ buyer.phone }}{% endif %}",
			),
		],
		bold_header=True,
		page_break_before=True,
		keep_rows_together=True,
	)
	_add_two_column_lines(
		doc,
		[
			("Поставщик:", "Покупатель:"),
			("{{ seller.company_name }}", "{{ buyer.company_name }}"),
			(
				"{{ supply_contract.officials[0].position or '_________________(ДОЛЖНОСТЬ)' }}",
				"_________________(ДОЛЖНОСТЬ)",
			),
			("", ""),
			("_________________", "_________________"),
			(
				"/{% if supply_contract.officials[0].full_name %}{{ supply_contract.officials[0].full_name }}{% else %}_____________(ФИО){% endif %}/",
				"/{% if buyer.full_name %}{{ buyer.full_name }}{% else %}_____________(ФИО){% endif %}/",
			),
			("«____» _______________ 20__г.", "«____» _______________ 20__г."),
			("М.П.", "М.П."),
		],
		bold_header=True,
		keep_rows_together=True,
	)
	path.parent.mkdir(parents=True, exist_ok=True)
	doc.save(str(path))
	print("Wrote", path)


def main() -> None:
	root = Path(__file__).resolve().parents[1]
	docx_dir = root / "app" / "templates" / "docx"
	write_bill_payment(docx_dir / "bill.docx")
	write_bill_variant(docx_dir / "bill_contract.docx", "Счёт (договор)")
	write_bill_variant(docx_dir / "bill_offer.docx", "Счёт (оферта)")
	write_supply_contract(docx_dir / "supply_contract.docx")


if __name__ == "__main__":
	main()
