#!/usr/bin/env python3
"""Сборка PDF инструкции по проверке ТЗ «Договор на перевозку грузов»."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
	ListFlowable,
	ListItem,
	Paragraph,
	SimpleDocTemplate,
	Spacer,
	Table,
	TableStyle,
)

OUT = Path(__file__).with_name("Priemka_TZ_Dogovor_perevozki_gruzov.pdf")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

pdfmetrics.registerFont(TTFont("DejaVu", FONT))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_B))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1", fontName="DejaVu-Bold", fontSize=15, leading=19, spaceAfter=8))
styles.add(
	ParagraphStyle(
		name="H2",
		fontName="DejaVu-Bold",
		fontSize=11.5,
		leading=14,
		spaceBefore=12,
		spaceAfter=6,
	)
)
styles.add(
	ParagraphStyle(
		name="H3",
		fontName="DejaVu-Bold",
		fontSize=10,
		leading=13,
		spaceBefore=8,
		spaceAfter=3,
	)
)
styles.add(ParagraphStyle(name="Body", fontName="DejaVu", fontSize=9.5, leading=13, spaceAfter=5))
styles.add(
	ParagraphStyle(
		name="Small",
		fontName="DejaVu",
		fontSize=8.5,
		leading=11,
		textColor=colors.HexColor("#444444"),
		spaceAfter=8,
	)
)
styles.add(ParagraphStyle(name="Cell", fontName="DejaVu", fontSize=8.5, leading=11))
styles.add(ParagraphStyle(name="CellB", fontName="DejaVu-Bold", fontSize=8.5, leading=11))


def P(text: str, style: str = "Body") -> Paragraph:
	return Paragraph(text, styles[style])


def table(headers: list[str], rows: list[list[str]], col_widths=None) -> Table:
	data = [[P(h, "CellB") for h in headers]]
	for row in rows:
		data.append([P(c, "Cell") for c in row])
	t = Table(data, colWidths=col_widths, repeatRows=1)
	t.setStyle(
		TableStyle(
			[
				("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
				("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
				("VALIGN", (0, 0), (-1, -1), "TOP"),
				("LEFTPADDING", (0, 0), (-1, -1), 4),
				("RIGHTPADDING", (0, 0), (-1, -1), 4),
				("TOPPADDING", (0, 0), (-1, -1), 3),
				("BOTTOMPADDING", (0, 0), (-1, -1), 3),
			]
		)
	)
	return t


def steps(items: list[str]) -> ListFlowable:
	return ListFlowable(
		[ListItem(P(i, "Body"), leftIndent=6) for i in items],
		bulletType="1",
		start="1",
		leftIndent=12,
	)


story = []
story.append(P("Инструкция по проверке: договор на перевозку грузов", "H1"))
story.append(
	P(
		"Сайт: <b>https://tradesynergy.ru</b><br/>"
		"Дата проверки: 04.11.2026",
		"Small",
	)
)

story.append(P("1. Тестовые учётки", "H2"))
story.append(P("Пароль для всех учёток: <b>123456</b>", "Body"))
story.append(
	table(
		["Роль", "Email", "Компания", "Назначение"],
		[
			["Поставщик", "seller@gmail.com", "ООО Поставщик Тест", "Создаёт документы перевозки и экспедиции"],
			["Покупатель", "buyer@gmail.com", "ООО Покупатель Тест", "Закупки, просмотр сканов в чате"],
			["Перевозчик", "carrier@gmail.com", "ООО Перевозчик Тест", "Организация в списке перевозчиков продавца"],
			["Экспедитор", "forwarder@gmail.com", "ООО Экспедитор Тест", "Для бланков экспедиции"],
		],
		col_widths=[28 * mm, 42 * mm, 45 * mm, 63 * mm],
	)
)
story.append(
	P(
		"Документы создаёт продавец (<b>seller@gmail.com</b>). "
		"В личном кабинете продавца в разделе «Перевозчики» должны быть "
		"ООО Перевозчик Тест и ООО Экспедитор Тест.",
		"Body",
	)
)

story.append(P("2. Куда заходить", "H2"))
story.append(
	table(
		["Раздел", "Адрес"],
		[
			["Вход", "https://tradesynergy.ru/auth/login"],
			["Продажи → Товары", "https://tradesynergy.ru/profile/sales"],
			["Редактор документов", "из ячейки «Договор перевозки», вкладка «Договор»"],
			["Поиск транспорта", "кнопка «Найти транспорт» в строке заказа"],
		],
		col_widths=[50 * mm, 128 * mm],
	)
)
story.append(
	P(
		"Тестовые заказы продавца: <b>00001–00005</b>. "
		"Для создания документов удобен заказ <b>№ 00005</b>.",
		"Body",
	)
)

story.append(P("3. Документы в пакете", "H2"))
story.append(
	table(
		["№", "Документ", "Примечание"],
		[
			["1", "Договор перевозки грузов", "Заказчик и перевозчик"],
			["2", "Заявка к договору", "Приложение; нужен договор перевозки"],
			["3", "Договор-заявка", "Разовая перевозка"],
			["4", "Договор транспортной экспедиции", "Клиент и экспедитор"],
			["5", "Поручение экспедитору", "Строгий бланк; нужен договор экспедиции"],
			["6", "Экспедиторская расписка", "Строгий бланк"],
			["7", "Складская расписка", "Строгий бланк"],
		],
		col_widths=[10 * mm, 70 * mm, 98 * mm],
	)
)

story.append(P("4. Порядок проверки", "H2"))

story.append(P("4.1. Создание документа из Продаж", "H3"))
story.append(
	steps(
		[
			"Войти как seller@gmail.com / 123456.",
			"Открыть Продажи → таблица «Товары».",
			"В колонке «Договор перевозки» нажать «Создать док. перевозки».",
			"В диалоге должны быть семь типов документов.",
			"Выбрать «Договор перевозки», организацию-перевозчика и создать новый документ "
			"(либо привязать существующий).",
			"В ячейке появляются номер и дата; открывается редактор на вкладке «Договор».",
		]
	)
)

story.append(P("4.2. Бланк договора перевозки", "H3"))
story.append(
	steps(
		[
			"В редакторе нажать «Редактировать», затем «Заполнить данными».",
			"Проверить реквизиты заказчика и перевозчика, текст договора.",
			"Проверить печать и выгрузку DOC / PDF.",
		]
	)
)

story.append(P("4.3. Заявка к договору", "H3"))
story.append(
	steps(
		[
			"Снова «Создать док. перевозки» → тип «Заявка».",
			"Если на заказе нет договора перевозки — система сообщает, что нужен родительский договор.",
			"Если договор есть — создаётся заявка с номером 1, 2, 3… и отображается в ячейке.",
			"В бланке: шапка «приложение к договору», таблица груз/транспорт, реквизиты.",
		]
	)
)

story.append(P("4.4. Договор-заявка и экспедиция", "H3"))
story.append(
	steps(
		[
			"Тип «Договор-заявка» — создаётся без списка старых договоров.",
			"Тип «Договор экспедиции» — роли «Клиент» / «Экспедитор», кнопка «Заполнить данными».",
		]
	)
)

story.append(P("4.5. Поручение и расписки", "H3"))
story.append(
	steps(
		[
			"Сначала на заказе должен быть договор экспедиции.",
			"Создать поручение экспедитору, экспедиторскую или складскую расписку.",
			"«Заполнить данными» подставляет индекс, ИНН, адреса и ФИО подписанта.",
			"На складской расписке — шапка Минтранса и подпись экспедитора.",
		]
	)
)

story.append(P("4.6. Поиск транспорта", "H3"))
story.append(
	steps(
		[
			"В строке заказа нажать «Найти транспорт».",
			"Открывается поиск; возврат «К продажам» возвращает в таблицу.",
		]
	)
)

story.append(P("5. Что проверено на сайте 04.11.2026", "H2"))
story.append(
	table(
		["Проверка", "Результат"],
		[
			["Вход seller / buyer", "работает"],
			["Продажи, колонка «Договор перевозки»", "работает"],
			["Создание договора и привязка к заказу 00005", "в ячейке видны номер и тип"],
			["Создание заявки", "номер 1 отображается в ячейке"],
			["Редактор, вкладка «Договор»", "открывается корректно"],
			["Выгрузка DOC и PDF", "файлы скачиваются"],
			["Сертификат сайта (tradesynergy.ru и www)", "действует до 02.02.2027"],
		],
		col_widths=[100 * mm, 78 * mm],
	)
)

story.append(P("6. Этапы работ", "H2"))
story.append(
	table(
		["Этап", "Содержание", "Статус"],
		[
			["1", "Каркас: семь типов документов, диалог, ячейка в Продажах", "готов"],
			["2", "Бланк договора перевозки", "готов"],
			["3", "Заявка к договору", "готов"],
			["4", "Договор-заявка и договор экспедиции", "готов"],
			["5", "Поручение, экспедиторская и складская расписки", "готов"],
		],
		col_widths=[14 * mm, 124 * mm, 40 * mm],
	)
)

story.append(Spacer(1, 8))
story.append(
	P(
		"<b>Кратко:</b> https://tradesynergy.ru · seller@gmail.com / 123456 · "
		"Продажи → «Договор перевозки» → вкладка «Договор» в редакторе.",
		"Body",
	)
)

doc = SimpleDocTemplate(
	str(OUT),
	pagesize=A4,
	leftMargin=14 * mm,
	rightMargin=14 * mm,
	topMargin=14 * mm,
	bottomMargin=14 * mm,
	title="Инструкция по проверке — договор на перевозку грузов",
	author="TradeSynergy",
)
doc.build(story)
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
