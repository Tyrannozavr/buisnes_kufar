"""Генерация .docx для бланков transport_document из payload_json (python-docx)."""

from __future__ import annotations

import io
import re
from datetime import datetime
from typing import Any, Optional

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from app.api.purchases.docx_plain_text import html_to_plain_text

_MONTHS_RU = {
	1: "января",
	2: "февраля",
	3: "марта",
	4: "апреля",
	5: "мая",
	6: "июня",
	7: "июля",
	8: "августа",
	9: "сентября",
	10: "октября",
	11: "ноября",
	12: "декабря",
}

DOC_TITLES: dict[str, str] = {
	"carriage_contract": "ДОГОВОР ПЕРЕВОЗКИ ГРУЗОВ",
	"carriage_application": "ЗАЯВКА К ДОГОВОРУ ПЕРЕВОЗКИ ГРУЗОВ",
	"carriage_order": "ДОГОВОР-ЗАЯВКА НА ПЕРЕВОЗКУ ГРУЗОВ",
	"expedition_contract": "ДОГОВОР ТРАНСПОРТНОЙ ЭКСПЕДИЦИИ",
	"forwarder_assignment": "ПОРУЧЕНИЕ ЭКСПЕДИТОРУ",
	"forwarder_receipt": "ЭКСПЕДИТОРСКАЯ РАСПИСКА",
	"warehouse_receipt": "СКЛАДСКАЯ РАСПИСКА",
}

_STRICT_TYPES = frozenset(
	{"forwarder_assignment", "forwarder_receipt", "warehouse_receipt"}
)


def _as_dict(value: Any) -> dict[str, Any]:
	return value if isinstance(value, dict) else {}


def _s(value: Any) -> str:
	if value is None:
		return ""
	return str(value).strip()


def format_doc_date(value: Optional[datetime], *, style2: bool = True) -> str:
	"""Дата бланка: «04» ноября 2026 или 04.11.2026."""
	if value is None:
		return "«____» _______________ 20____"
	if style2:
		month = _MONTHS_RU.get(value.month, "_______________")
		return f"«{value.day:02d}» {month} {value.year}"
	return f"{value.day:02d}.{value.month:02d}.{value.year}"


def _set_run_font(run, *, bold: bool = False, size_pt: float = 12) -> None:
	run.bold = bold
	run.font.size = Pt(size_pt)
	run.font.name = "Times New Roman"
	r = run._element
	rPr = r.get_or_add_rPr()
	rFonts = rPr.get_or_add_rFonts()
	rFonts.set(qn("w:eastAsia"), "Times New Roman")


def _configure_document(doc: Document) -> None:
	section = doc.sections[0]
	section.top_margin = Cm(1.5)
	section.bottom_margin = Cm(1.5)
	section.left_margin = Cm(2)
	section.right_margin = Cm(1.5)
	style = doc.styles["Normal"]
	style.font.name = "Times New Roman"
	style.font.size = Pt(12)
	style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")


def _add_paragraph(
	doc: Document,
	text: str = "",
	*,
	bold: bool = False,
	center: bool = False,
	space_after: float = 6,
) -> None:
	p = doc.add_paragraph()
	pf = p.paragraph_format
	pf.space_after = Pt(space_after)
	pf.space_before = Pt(0)
	pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
	if center:
		p.alignment = WD_ALIGN_PARAGRAPH.CENTER
	if text:
		run = p.add_run(text)
		_set_run_font(run, bold=bold)


def _add_plain_lines(doc: Document, text: str) -> None:
	cleaned = html_to_plain_text(text) if text else ""
	if not cleaned:
		return
	for line in cleaned.splitlines():
		_add_paragraph(doc, line, space_after=4)


def _format_legal_address(index: str, legal_address: str) -> str:
	idx = _s(index)
	addr = _s(legal_address)
	if idx and addr:
		if addr.startswith(idx):
			return addr
		return f"{idx}, {addr}"
	return addr or idx


def _party_preamble(
	party: dict[str, Any],
	*,
	role_label: str,
	side_phrase: str,
) -> str:
	full_name = _s(party.get("fullName")) or "________________"
	company_type = _s(party.get("companyType"))
	if company_type == "ИП":
		ogrn = _s(party.get("ogrn")) or "___________"
		return (
			f"{full_name}, далее — «{role_label}», зарегистрированный в реестре "
			f"индивидуальных предпринимателей под № {ogrn}, {side_phrase}"
		)
	position = _s(party.get("officialPosition")) or "_______________"
	name = _s(party.get("officialName")) or "_______________"
	foundation = _s(party.get("foundationKind")) or "Устава"
	title = _s(party.get("foundationTitle"))
	foundation_part = f"{foundation} {title}".strip() if title else foundation
	return (
		f"{full_name}, далее — «{role_label}», от имени которого действует "
		f"{position} {name}, действующего(ей) на основании {foundation_part}, {side_phrase}"
	)


def _party_details_lines(party: dict[str, Any]) -> list[str]:
	lines = [
		_s(party.get("fullName")) or "—",
		_format_legal_address(_s(party.get("index")), _s(party.get("legalAddress"))),
	]
	inn = _s(party.get("inn"))
	if inn:
		lines.append(f"ИНН {inn}")
	kpp = _s(party.get("kpp"))
	if kpp:
		lines.append(f"КПП {kpp}")
	account = _s(party.get("accountNumber"))
	bank = _s(party.get("bankName"))
	if account or bank:
		lines.append(f"Рас/счет № {account} в {bank}".strip())
	corr = _s(party.get("correspondentBankAccount"))
	if corr:
		lines.append(corr)
	bic = _s(party.get("bic"))
	if bic:
		lines.append(f"БИК {bic}")
	official = _s(party.get("officialName")) or "____________"
	lines.append(f"________________ / {official} /")
	lines.append("М.П.")
	return [line for line in lines if line]


def _add_two_column_details(
	doc: Document,
	left_title: str,
	left_party: dict[str, Any],
	right_title: str,
	right_party: dict[str, Any],
	*,
	show_left: bool,
	show_right: bool,
) -> None:
	if not show_left and not show_right:
		return
	table = doc.add_table(rows=2, cols=2 if show_left and show_right else 1)
	table.autofit = True
	cells_row0 = table.rows[0].cells
	cells_row1 = table.rows[1].cells
	if show_left and show_right:
		cells_row0[0].text = left_title
		cells_row0[1].text = right_title
		cells_row1[0].text = "\n".join(_party_details_lines(left_party))
		cells_row1[1].text = "\n".join(_party_details_lines(right_party))
	elif show_left:
		cells_row0[0].text = left_title
		cells_row1[0].text = "\n".join(_party_details_lines(left_party))
	else:
		cells_row0[0].text = right_title
		cells_row1[0].text = "\n".join(_party_details_lines(right_party))
	for row in table.rows:
		for cell in row.cells:
			for p in cell.paragraphs:
				for run in p.runs:
					_set_run_font(run, bold=(":" in (p.text or "") and p is cell.paragraphs[0]))


def _add_label_value_table(doc: Document, rows: list[tuple[str, str]]) -> None:
	table = doc.add_table(rows=len(rows), cols=3)
	table.style = "Table Grid"
	for idx, (label, value) in enumerate(rows):
		cells = table.rows[idx].cells
		cells[0].text = str(idx + 1)
		cells[1].text = label
		cells[2].text = value or "—"
		for cell in cells:
			for p in cell.paragraphs:
				for run in p.runs:
					_set_run_font(run, size_pt=11)


def _cargo_table_rows(snapshot: Any) -> list[tuple[str, str]]:
	if not isinstance(snapshot, dict):
		return []
	# Snapshot хранит label → value (как rowsToSnapshot на фронте).
	rows: list[tuple[str, str]] = []
	for key, value in snapshot.items():
		rows.append((_s(key), _s(value)))
	return rows


def _strict_party_block(party: dict[str, Any]) -> str:
	lines = [
		_s(party.get("fullName")),
		_format_legal_address(_s(party.get("index")), _s(party.get("legalAddress"))),
	]
	inn = _s(party.get("inn"))
	if inn:
		lines.append(f"ИНН {inn}")
	return "\n".join(line for line in lines if line) or "—"


def _strict_rows(
	doc_type: str,
	payload: dict[str, Any],
	*,
	number: str,
	date_label: str,
) -> list[tuple[str, str]]:
	shipper = _as_dict(payload.get("shipper"))
	client = _as_dict(payload.get("client"))
	consignee = _as_dict(payload.get("consignee"))
	forwarder = _as_dict(payload.get("forwarder"))
	sig = " / ".join(
		part
		for part in (_s(payload.get("signaturePosition")), _s(payload.get("signatureName")))
		if part
	) or "—"
	base = [("Дата", date_label), ("Номер", number or "—")]
	if doc_type == "forwarder_assignment":
		return base + [
			("Грузоотправитель", _strict_party_block(shipper)),
			("Клиент", _strict_party_block(client)),
			("Грузополучатель", _strict_party_block(consignee)),
			("Экспедитор", _strict_party_block(forwarder)),
			("Уведомить о прибытии груза", _s(payload.get("notifyParty")) or "—"),
			("Страна происхождения груза", _s(payload.get("originCountry")) or "—"),
			("Товары готовы к отправке (место, дата)", _s(payload.get("readyToShip")) or "—"),
			("Вид транспорта", _s(payload.get("transportMode")) or "—"),
			("Пункт назначения", _s(payload.get("destination")) or "—"),
			("Страхование", _s(payload.get("insurance")) or "—"),
			("Товарный код", _s(payload.get("commodityCode")) or "—"),
			("Маркировка", _s(payload.get("marking")) or "—"),
			("Количество мест, вид упаковки", _s(payload.get("placesPackaging")) or "—"),
			("Вес брутто / нетто, кг", _s(payload.get("weightGrossNet")) or "—"),
			("Объём", _s(payload.get("volume")) or "—"),
			("Стоимость", _s(payload.get("value")) or "—"),
			("Размер упаковки", _s(payload.get("packageSize")) or "—"),
			("Требуемые документы", _s(payload.get("requiredDocs")) or "—"),
			("Особые отметки", _s(payload.get("notes")) or "—"),
			("Подпись клиента", sig),
		]
	if doc_type == "forwarder_receipt":
		return base + [
			("Грузоотправитель", _strict_party_block(shipper)),
			("Клиент", _strict_party_block(client)),
			("Экспедитор", _strict_party_block(forwarder)),
			("Страна происхождения груза", _s(payload.get("originCountry")) or "—"),
			("Товарный код", _s(payload.get("commodityCode")) or "—"),
			("Маркировка", _s(payload.get("marking")) or "—"),
			("Количество мест, вид упаковки", _s(payload.get("placesPackaging")) or "—"),
			("Вес брутто / нетто, кг", _s(payload.get("weightGrossNet")) or "—"),
			("Объём", _s(payload.get("volume")) or "—"),
			("Стоимость", _s(payload.get("value")) or "—"),
			("Размер упаковки", _s(payload.get("packageSize")) or "—"),
			("Условия", _s(payload.get("terms")) or "—"),
			("Особые отметки", _s(payload.get("notes")) or "—"),
			("Подпись клиента", sig),
		]
	return base + [
		("Клиент", _strict_party_block(client)),
		("Экспедитор", _strict_party_block(forwarder)),
		("Склад", _s(payload.get("warehouse")) or "—"),
		("Страна происхождения груза", _s(payload.get("originCountry")) or "—"),
		("Страхование", _s(payload.get("insurance")) or "—"),
		("Товарный код", _s(payload.get("commodityCode")) or "—"),
		("Маркировка", _s(payload.get("marking")) or "—"),
		("Количество мест, вид упаковки", _s(payload.get("placesPackaging")) or "—"),
		("Вес брутто / нетто, кг", _s(payload.get("weightGrossNet")) or "—"),
		("Объём", _s(payload.get("volume")) or "—"),
		("Стоимость", _s(payload.get("value")) or "—"),
		("Размер упаковки", _s(payload.get("packageSize")) or "—"),
		("Условия", _s(payload.get("terms")) or "—"),
		("Особые отметки", _s(payload.get("notes")) or "—"),
		("Подпись экспедитора", sig),
	]


def _build_framework_like(
	doc: Document,
	*,
	title: str,
	number: str,
	city: str,
	date_label: str,
	left_role: str,
	right_role: str,
	left_party: dict[str, Any],
	right_party: dict[str, Any],
	body_html: str,
	show_left: bool,
	show_right: bool,
	closing: str,
) -> None:
	_add_paragraph(doc, f"{title} № {number or '___'}", bold=True, center=True, space_after=10)
	meta = doc.add_paragraph()
	meta.paragraph_format.space_after = Pt(8)
	left_run = meta.add_run(f"г. {_s(city) or '_______________'}")
	_set_run_font(left_run)
	meta.add_run("\t")
	right_run = meta.add_run(date_label)
	_set_run_font(right_run)

	_add_paragraph(
		doc,
		_party_preamble(left_party, role_label=left_role, side_phrase="с одной стороны,"),
		space_after=6,
	)
	_add_paragraph(
		doc,
		_party_preamble(right_party, role_label=right_role, side_phrase=closing),
		space_after=10,
	)
	_add_plain_lines(doc, body_html)
	_add_two_column_details(
		doc,
		f"{left_role.upper()}:",
		left_party,
		f"{right_role.upper()}:",
		right_party,
		show_left=show_left,
		show_right=show_right,
	)


def build_transport_document_docx_bytes(
	*,
	doc_type: str,
	number: str,
	date: Optional[datetime],
	payload_json: Optional[dict[str, Any]],
	parent_number: Optional[str] = None,
	parent_date: Optional[datetime] = None,
) -> bytes:
	"""Собрать OOXML .docx из типа документа и payload_json."""
	payload = _as_dict(payload_json)
	doc = Document()
	_configure_document(doc)
	title = DOC_TITLES.get(doc_type, "ДОКУМЕНТ ПЕРЕВОЗКИ")
	date_label = format_doc_date(date, style2=True)
	parent_date_label = format_doc_date(parent_date, style2=True)

	if doc_type in _STRICT_TYPES:
		if doc_type == "warehouse_receipt":
			_add_paragraph(
				doc,
				"Приложение № 3 к приказу Минтранса РФ от 11 февраля 2008 г. № 23",
				center=True,
				space_after=4,
			)
		_add_paragraph(
			doc,
			(
				f"Приложение к Договору транспортной экспедиции № "
				f"{_s(parent_number) or '___'} от {parent_date_label} г."
			),
			center=True,
			space_after=8,
		)
		_add_paragraph(doc, title, bold=True, center=True, space_after=10)
		_add_label_value_table(
			doc,
			_strict_rows(doc_type, payload, number=_s(number), date_label=date_label),
		)
	elif doc_type == "carriage_contract":
		_build_framework_like(
			doc,
			title=title,
			number=_s(number),
			city=_s(payload.get("city")),
			date_label=date_label,
			left_role="Заказчик",
			right_role="Перевозчик",
			left_party=_as_dict(payload.get("customer")),
			right_party=_as_dict(payload.get("carrier")),
			body_html=_s(payload.get("bodyHtml")),
			show_left=payload.get("customerDetailsCheck") is not False,
			show_right=payload.get("carrierDetailsCheck") is not False,
			closing=(
				"с другой стороны, далее совместно именуемые «Стороны», заключили настоящий "
				"Договор перевозки грузов (далее — «Договор») о нижеследующем:"
			),
		)
	elif doc_type == "expedition_contract":
		_build_framework_like(
			doc,
			title=title,
			number=_s(number),
			city=_s(payload.get("city")),
			date_label=date_label,
			left_role="Клиент",
			right_role="Экспедитор",
			left_party=_as_dict(payload.get("client")),
			right_party=_as_dict(payload.get("forwarder")),
			body_html=_s(payload.get("bodyHtml")),
			show_left=payload.get("clientDetailsCheck") is not False,
			show_right=payload.get("forwarderDetailsCheck") is not False,
			closing=(
				"с другой стороны, далее совместно именуемые «Стороны», заключили настоящий "
				"Договор транспортной экспедиции (далее — «Договор») о нижеследующем:"
			),
		)
	elif doc_type == "carriage_application":
		_add_paragraph(
			doc,
			(
				f"Приложение к Договору перевозки грузов № {_s(parent_number) or '___'} "
				f"от {parent_date_label} г."
			),
			center=True,
			space_after=6,
		)
		_add_paragraph(
			doc,
			f"{title} № {_s(number) or '___'}",
			bold=True,
			center=True,
			space_after=10,
		)
		_add_paragraph(doc, f"Дата: {date_label}", space_after=8)
		cargo_rows = _cargo_table_rows(payload.get("cargoTableSnapshot"))
		if cargo_rows:
			_add_paragraph(doc, "Данные о грузе и транспорте", bold=True, space_after=4)
			_add_label_value_table(doc, cargo_rows)
		_add_paragraph(doc, "Дополнительные условия", bold=True, space_after=4)
		_add_plain_lines(doc, _s(payload.get("extraTermsHtml")))
		_add_two_column_details(
			doc,
			"ЗАКАЗЧИК:",
			_as_dict(payload.get("customer")),
			"ПЕРЕВОЗЧИК:",
			_as_dict(payload.get("carrier")),
			show_left=payload.get("customerDetailsCheck") is not False,
			show_right=payload.get("carrierDetailsCheck") is not False,
		)
	elif doc_type == "carriage_order":
		_add_paragraph(
			doc,
			f"{title} № {_s(number) or '___'}",
			bold=True,
			center=True,
			space_after=10,
		)
		city = _s(payload.get("city"))
		meta = doc.add_paragraph()
		meta.paragraph_format.space_after = Pt(8)
		_set_run_font(meta.add_run(f"г. {city or '_______________'}"))
		meta.add_run("\t")
		preamble_date = _s(payload.get("preambleDate")) or date_label
		# ISO → style2, иначе как есть
		if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", preamble_date):
			try:
				preamble_dt = datetime.fromisoformat(preamble_date[:10])
				preamble_date = format_doc_date(preamble_dt, style2=True)
			except ValueError:
				pass
		_set_run_font(meta.add_run(preamble_date))
		_add_paragraph(
			doc,
			_party_preamble(
				_as_dict(payload.get("customer")),
				role_label="Заказчик",
				side_phrase="с одной стороны,",
			),
			space_after=6,
		)
		_add_paragraph(
			doc,
			_party_preamble(
				_as_dict(payload.get("carrier")),
				role_label="Перевозчик",
				side_phrase=(
					"с другой стороны, заключили настоящую договор-заявку о нижеследующем:"
				),
			),
			space_after=8,
		)
		_add_paragraph(
			doc,
			(
				"Перевозчик принимает на себя обязательство перевезти груз на условиях "
				"настоящей заявки, а Заказчик — оплатить перевозку."
			),
			space_after=8,
		)
		cargo_rows = _cargo_table_rows(payload.get("cargoTableSnapshot"))
		if cargo_rows:
			_add_paragraph(doc, "Данные о грузе и транспорте", bold=True, space_after=4)
			_add_label_value_table(doc, cargo_rows)
		_add_paragraph(doc, "Условия", bold=True, space_after=4)
		_add_plain_lines(doc, _s(payload.get("extraTermsHtml")))
		_add_two_column_details(
			doc,
			"ЗАКАЗЧИК:",
			_as_dict(payload.get("customer")),
			"ПЕРЕВОЗЧИК:",
			_as_dict(payload.get("carrier")),
			show_left=payload.get("customerDetailsCheck") is not False,
			show_right=payload.get("carrierDetailsCheck") is not False,
		)
	else:
		_add_paragraph(doc, f"{title} № {_s(number) or '___'}", bold=True, center=True)
		_add_paragraph(doc, f"Дата: {date_label}")
		_add_paragraph(doc, "Данные бланка:", bold=True)
		_add_paragraph(doc, str(payload)[:4000] if payload else "—")

	buf = io.BytesIO()
	doc.save(buf)
	return buf.getvalue()
