"""Лёгкая санация HTML-фрагментов без внешних зависимостей."""
from __future__ import annotations

import re
from typing import Any

_BLOCKED_TAGS = re.compile(
	r"<\s*/?\s*(script|iframe|object|embed|link|meta|base|form|svg|math)\b[^>]*>",
	re.I,
)
_EVENT_ATTR = re.compile(r"\son\w+\s*=\s*(['\"]).*?\1|\son\w+\s*=\s*[^\s>]+", re.I)
_JS_URL = re.compile(
	r"""(?P<attr>href|src|xlink:href|action)\s*=\s*(?P<q>['"]?)\s*javascript:[^'">\s]*(?P=q)?""",
	re.I,
)

_HTML_KEYS = frozenset({"extraTermsHtml", "bodyHtml", "extra_terms_html", "body_html"})
_MAX_PAYLOAD_CHARS = 200_000


def sanitize_html_fragment(html: str) -> str:
	if not html:
		return html
	out = _BLOCKED_TAGS.sub("", html)
	out = _EVENT_ATTR.sub("", out)
	out = _JS_URL.sub(r'\g<attr>="#"', out)
	return out


def sanitize_payload_json(payload: dict[str, Any] | None) -> dict[str, Any] | None:
	if not payload:
		return payload
	out: dict[str, Any] = {}
	for key, value in payload.items():
		if key in _HTML_KEYS and isinstance(value, str):
			out[key] = sanitize_html_fragment(value)
		elif isinstance(value, dict):
			out[key] = sanitize_payload_json(value)  # type: ignore[assignment]
		else:
			out[key] = value
	return out


def assert_payload_size(payload: dict[str, Any] | None) -> None:
	if payload is None:
		return
	# грубая оценка без полного dumps (быстрее на больших dict)
	approx = len(str(payload))
	if approx > _MAX_PAYLOAD_CHARS:
		raise ValueError(f"payload_json слишком большой (>{_MAX_PAYLOAD_CHARS} символов)")
