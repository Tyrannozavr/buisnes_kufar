"""Форматирование строк поставщика/покупателя для счёта (§5 ТЗ)."""


def strip_leading_org_type(company_name: str, company_type: str | None) -> str:
	name = (company_name or "").strip()
	org_type = (company_type or "").strip()
	if not org_type or not name:
		return name
	if name.upper().startswith(org_type.upper()):
		return name[len(org_type) :].strip()
	return name


def format_legal_address_for_party(index: str | None, legal_address: str | None) -> str:
	addr = (legal_address or "").strip()
	idx = (index or "").strip()
	if not addr:
		return idx
	if idx and (addr.startswith(idx) or addr.startswith(f"{idx},")):
		return addr
	if idx:
		return f"{idx}, {addr}"
	return addr


def format_company_party_line(party: dict) -> str:
	name = party.get("company_name") or ""
	if not name:
		return ""
	org_type = (party.get("company_type") or "").strip()
	short_name = strip_leading_org_type(name, org_type or None)
	full_name = f"{org_type} {short_name}".strip() if org_type else short_name
	address = format_legal_address_for_party(party.get("index"), party.get("legal_address"))
	parts = [full_name, party.get("inn", ""), party.get("kpp", ""), address]
	return ", ".join(str(p).strip() for p in parts if p not in (None, ""))
