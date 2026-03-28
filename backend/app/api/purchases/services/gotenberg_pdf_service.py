"""Конвертация DOCX → PDF через Gotenberg (LibreOffice)."""
from __future__ import annotations

import time
from typing import Optional

import httpx

from app.core.config import settings
from app_logging.logger import logger

GOTENBERG_LIBREOFFICE_PATH = "/forms/libreoffice/convert"
DOCX_MEDIA = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class PdfConversionNotConfiguredError(Exception):
	"""Нет GOTENBERG_URL — конвертация недоступна."""


class PdfConversionFailedError(Exception):
	"""Gotenberg вернул ошибку или непустой ответ без PDF."""


def _gotenberg_base_url() -> Optional[str]:
	url = settings.GOTENBERG_URL
	if not url or not str(url).strip():
		return None
	return str(url).rstrip("/")


async def convert_docx_bytes_to_pdf(
	docx_bytes: bytes,
	*,
	source_filename: str = "document.docx",
) -> bytes:
	"""
	POST multipart на Gotenberg /forms/libreoffice/convert, поле files.
	Raises:
		PdfConversionNotConfiguredError: GOTENBERG_URL не задан
		PdfConversionFailedError: HTTP ошибка или ответ не похож на PDF
		ValueError: превышен лимит размера DOCX
	"""
	base = _gotenberg_base_url()
	if not base:
		raise PdfConversionNotConfiguredError("GOTENBERG_URL is not set")

	max_bytes = settings.GOTENBERG_MAX_DOCX_BYTES
	if len(docx_bytes) > max_bytes:
		raise ValueError(f"DOCX exceeds max size for PDF conversion ({max_bytes} bytes)")

	url = f"{base}{GOTENBERG_LIBREOFFICE_PATH}"
	timeout = httpx.Timeout(settings.GOTENBERG_TIMEOUT_SECONDS)

	t0 = time.perf_counter()
	try:
		async with httpx.AsyncClient(timeout=timeout) as client:
			resp = await client.post(
				url,
				files={
					"files": (source_filename, docx_bytes, DOCX_MEDIA),
				},
			)
	except httpx.TimeoutException as e:
		logger.exception("Gotenberg timeout after %.1fs", settings.GOTENBERG_TIMEOUT_SECONDS)
		raise PdfConversionFailedError("PDF conversion timed out") from e
	except httpx.RequestError as e:
		logger.exception("Gotenberg request failed: %s", e)
		raise PdfConversionFailedError("PDF conversion service unreachable") from e

	elapsed = time.perf_counter() - t0
	if resp.status_code >= 400:
		body_preview = (resp.text or "")[:500]
		logger.error(
			"Gotenberg HTTP %s in %.2fs: %s",
			resp.status_code,
			elapsed,
			body_preview,
		)
		raise PdfConversionFailedError(f"PDF conversion failed (HTTP {resp.status_code})")

	data = resp.content
	if not data.startswith(b"%PDF"):
		logger.error("Gotenberg returned non-PDF (%d bytes) in %.2fs", len(data), elapsed)
		raise PdfConversionFailedError("PDF conversion returned invalid payload")

	logger.debug("Gotenberg PDF ok: %d bytes in %.2fs", len(data), elapsed)
	return data
