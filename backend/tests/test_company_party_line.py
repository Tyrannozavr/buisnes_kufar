from app.api.purchases.company_party_line import format_company_party_line, strip_leading_org_type


def test_strip_leading_org_type() -> None:
	assert strip_leading_org_type("ООО Поставщик Тест", "ООО") == "Поставщик Тест"


def test_format_company_party_line_no_duplicate_type_or_index() -> None:
	line = format_company_party_line(
		{
			"company_type": "ООО",
			"company_name": "ООО Поставщик Тест",
			"inn": "7707083893",
			"kpp": "770701001",
			"index": "101000",
			"legal_address": "101000, г. Москва, ул. Поставщика, д. 1",
		}
	)
	assert line == "ООО Поставщик Тест, 7707083893, 770701001, 101000, г. Москва, ул. Поставщика, д. 1"
