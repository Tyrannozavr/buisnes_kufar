"""Разовый анализ Jinja в supply_contract.docx."""
from __future__ import annotations

import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from jinja2 import Environment, TemplateSyntaxError

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def para_text(p: ET.Element) -> str:
	return "".join(t.text or "" for t in p.iter(f"{W}t"))


def main() -> None:
	path = Path(__file__).resolve().parents[1] / "app/templates/docx/supply_contract.docx"
	with zipfile.ZipFile(path) as z:
		xml = z.read("word/document.xml").decode("utf-8")
	root = ET.fromstring(xml)
	paras = list(root.iter(f"{W}p"))
	full = "".join(para_text(p) for p in paras)
	env = Environment()

	print(f"file: {path}")
	print(f"paragraphs: {len(paras)}")
	print()

	# docxtpl собирает XML-части; эмулируем: каждый абзац с jinja = отдельный compile unit
	jinja_paras: list[tuple[int, str]] = []
	for i, p in enumerate(paras, 1):
		t = para_text(p)
		if "{{" in t or "{%" in t:
			jinja_paras.append((i, t))

	print("=== SYNTAX ERRORS (per paragraph, merged runs) ===")
	for i, t in jinja_paras:
		try:
			env.parse(t)
		except TemplateSyntaxError as e:
			print(f"\nParagraph {i} (jinja virtual line ~{jinja_paras.index((i,t))+1}):")
			print(f"  error: {e.message}")
			print(f"  text: {t[:400]!r}")

	# line 52 from backend log
	if len(jinja_paras) >= 52:
		i, t = jinja_paras[51]
		print("\n=== BACKEND SAYS line 52 — likely this block ===")
		print(f"Paragraph index in doc: {i}")
		print(t[:500])

	print("\n=== SPLIT RUNS (partial tags) ===")
	for pi, p in enumerate(paras, 1):
		runs = [t.text for t in p.iter(f"{W}t") if t.text]
		if len(runs) <= 1:
			continue
		merged = "".join(runs)
		if "{{" not in merged and "{%" not in merged:
			continue
		bad = [
			r
			for r in runs
			if r.count("{{") != r.count("}}")
			or r.count("{%") != r.count("%}")
			or "{{%" in r
			or "%}}" in r
			or r.endswith("{%")
			or r.endswith("{{")
			or r.startswith("%}")
		]
		if bad:
			print(f"\nP{pi}:")
			print(f"  merged: {merged[:300]!r}")
			for r in bad[:6]:
				print(f"  bad run: {r!r}")

	print("\n=== REMAINING PATTERNS IN FULL TEXT ===")
	for pat, name in [
		(r"\{\{%", "{{%"),
		(r"%\}\}", "%}}"),
		(r"!==", "!=="),
		(r"supply_contract\.\s+spec", "space before spec"),
		(r"\{%\s*/", "{% / garbage"),
		(r"\{%\s*$", "dangling {%"),
	]:
		for m in re.finditer(pat, full):
			snip = full[max(0, m.start() - 20) : m.end() + 40]
			print(f"{name}: {snip!r}")


if __name__ == "__main__":
	main()
