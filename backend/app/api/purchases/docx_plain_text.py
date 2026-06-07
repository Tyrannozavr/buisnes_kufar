"""HTML из веб-редактора → plain text для docxtpl (Word не принимает теги внутри w:t)."""
from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Any

_BLOCK_BREAK_TAGS = frozenset(
	{
		"p",
		"div",
		"li",
		"tr",
		"h1",
		"h2",
		"h3",
		"h4",
		"h5",
		"h6",
		"blockquote",
	}
)


class _HtmlToPlainTextParser(HTMLParser):
	"""Собирает видимый текст; блочные теги → перенос строки."""

	def __init__(self) -> None:
		super().__init__(convert_charrefs=True)
		self._parts: list[str] = []

	def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
		if tag.lower() == "br":
			self._parts.append("\n")

	def handle_endtag(self, tag: str) -> None:
		if tag.lower() in _BLOCK_BREAK_TAGS:
			self._parts.append("\n")

	def handle_data(self, data: str) -> None:
		self._parts.append(data)

	def get_text(self) -> str:
		raw = "".join(self._parts)
		raw = unescape(raw)
		# схлопнуть пробелы в строке, убрать лишние пустые строки
		lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
		return "\n".join(line for line in lines if line)


def html_to_plain_text(value: Any) -> str:
	"""
	Преобразует HTML (TipTap) в plain text для подстановки в .docx.
	Без тегов — возвращает строку как есть (trim).
	"""
	if value is None:
		return ""
	if not isinstance(value, str):
		return str(value).strip()

	text = value.strip()
	if not text:
		return ""

	if "<" not in text and "&" not in text:
		return text

	parser = _HtmlToPlainTextParser()
	try:
		parser.feed(text)
		parser.close()
	except Exception:
		# fallback: вырезать теги грубо, если разметка битая
		stripped = re.sub(r"<[^>]+>", " ", text)
		return unescape(re.sub(r"[ \t]+", " ", stripped)).strip()

	return parser.get_text()


def sanitize_supply_contract_docx_fields(data: dict[str, Any]) -> None:
	"""Очищает HTML в текстовых полях supply_contract перед рендером docx."""
	supply_contract = data.get("supply_contract")
	if not isinstance(supply_contract, dict):
		return

	for key in ("supply_contract_text", "specification_text", "terms_text"):
		if key not in supply_contract:
			continue
		raw = supply_contract.get(key)
		if raw is None:
			continue
		supply_contract[key] = html_to_plain_text(raw)
