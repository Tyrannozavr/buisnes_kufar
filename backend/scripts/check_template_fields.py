from __future__ import annotations

import re
import zipfile
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "app/templates/docx/supply_contract.docx"
with zipfile.ZipFile(p) as z:
	text = "".join(
		t
		for t in re.findall(r"<w:t[^>]*>([^<]*)</w:t>", z.read("word/document.xml").decode("utf-8"))
	)

fields = sorted(set(re.findall(r"\{\{\s*([a-zA-Z0-9_.\[\]]+)\s*\}\}", text)))
print("PLACEHOLDERS:")
for f in fields:
	print(" ", f)
