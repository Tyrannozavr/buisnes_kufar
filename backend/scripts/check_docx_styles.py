from __future__ import annotations

import re
import zipfile
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "app/templates/docx/supply_contract.docx"
with zipfile.ZipFile(p) as z:
	xml = z.read("word/document.xml").decode("utf-8")
	styles = z.read("word/styles.xml").decode("utf-8")

print("=== document.xml ===")
print("w:color:", sorted(set(re.findall(r'w:color w:val="([^"]+)"', xml))))
print("w:pStyle:", sorted(set(re.findall(r'w:pStyle w:val="([^"]+)"', xml))))
print("w:rStyle:", sorted(set(re.findall(r'w:rStyle w:val="([^"]+)"', xml))))
print("w:highlight:", sorted(set(re.findall(r'w:highlight w:val="([^"]+)"', xml))))
print("hyperlinks:", xml.count("w:hyperlink"))

# preamble: text before supply_contract_text block
text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))
idx = text.find("seller_company")
print("\npreamble snippet:", text[max(0, idx - 100) : idx + 200])

print("\n=== styles.xml (color on paragraph/character styles) ===")
for m in re.finditer(
	r'w:styleId="([^"]+)"[^>]*>.*?w:name w:val="([^"]+)".*?(?:w:color w:val="([^"]+)")?',
	styles,
	re.DOTALL,
):
	sid, name, color = m.group(1), m.group(2), m.group(3)
	if color and color not in ("000000", "auto"):
		print(f"  {name} ({sid}): color {color}")

# Hyperlink style
if "Hyperlink" in styles:
	for m in re.finditer(r'w:styleId="Hyperlink"[\s\S]*?w:color w:val="([^"]+)"', styles):
		print("Hyperlink style color:", m.group(1))
