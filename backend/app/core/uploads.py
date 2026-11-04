"""Safe local file uploads: sanitize names, bound size, restrict extensions."""
from __future__ import annotations

import os
import re
import uuid
from typing import Iterable

from fastapi import HTTPException, UploadFile, status

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
CHAT_EXTENSIONS = IMAGE_EXTENSIONS | {
	".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv", ".zip", ".rar", ".7z",
}


def safe_extension(filename: str | None, *, allowed: Iterable[str]) -> str:
	ext = os.path.splitext(filename or "")[1].lower()
	allowed_set = {item.lower() for item in allowed}
	if ext not in allowed_set:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Unsupported file type. Allowed: {', '.join(sorted(allowed_set))}",
		)
	return ext


def sanitize_original_name(filename: str | None, *, max_len: int = 120) -> str:
	base = os.path.basename(filename or "file").strip() or "file"
	base = _SAFE_NAME_RE.sub("_", base)
	return base[:max_len]


def unique_filename(filename: str | None, *, allowed: Iterable[str]) -> tuple[str, str]:
	"""Return (stored_name, original_display_name)."""
	ext = safe_extension(filename, allowed=allowed)
	display = sanitize_original_name(filename)
	stored = f"{uuid.uuid4().hex}{ext}"
	return stored, display


async def read_upload_limited(file: UploadFile, *, max_bytes: int) -> bytes:
	data = await file.read(max_bytes + 1)
	if len(data) > max_bytes:
		raise HTTPException(
			status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
			detail=f"File too large (max {max_bytes // (1024 * 1024)} MB)",
		)
	return data
