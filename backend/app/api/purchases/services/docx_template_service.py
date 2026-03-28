"""Рендер шаблонов .docx через docxtpl."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docxtpl import DocxTemplate

from app.core.config import settings

# Файлы в DOCX_TEMPLATES_DIR — имена совпадают с шаблонами в репозитории
ORDER_DOCX_FILENAME = "order.docx"
BILL_DOCX_FILENAME = "bill.docx"
BILL_CONTRACT_DOCX_FILENAME = "bill_contract.docx"
BILL_OFFER_DOCX_FILENAME = "bill_offer.docx"


def resolve_docx_template_path(filename: str) -> Path:
	return settings.DOCX_TEMPLATES_DIR / filename


def render_docx_bytes(template_path: Path, context: dict) -> bytes:
	"""
	Подставляет context в шаблон и возвращает готовый .docx как bytes.
	Raises:
		FileNotFoundError: если файла шаблона нет.
	"""
	if not template_path.is_file():
		raise FileNotFoundError(f"DOCX template not found: {template_path}")
	tpl = DocxTemplate(str(template_path))
	tpl.render(context)
	buf = BytesIO()
	tpl.save(buf)
	buf.seek(0)
	return buf.read()
