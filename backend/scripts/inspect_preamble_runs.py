from __future__ import annotations

import re
import zipfile
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "app/templates/docx/supply_contract.docx"
with zipfile.ZipFile(p) as z:
	xml = z.read("word/document.xml").decode("utf-8")

# find runs with non-black color or underline
for m in re.finditer(r"<w:r[\s\S]*?</w:r>", xml):
	run = m.group()
	if "seller_company" not in run and "buyer" not in run and "{%" not in run:
		continue
	color = re.search(r'w:color w:val="([^"]+)"', run)
	underline = "w:u " in run or 'w:u w:val="single"' in run
	rstyle = re.search(r'w:rStyle w:val="([^"]+)"', run)
	if (color and color.group(1) not in ("000000", "auto")) or underline or rstyle:
		text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", run))
		print("RUN:", text[:80])
		if color:
			print("  color:", color.group(1))
		if rstyle:
			print("  rStyle:", rstyle.group(1))
		if underline:
			print("  underline")
