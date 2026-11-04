from app.core.html_sanitize import (
	assert_payload_size,
	sanitize_html_fragment,
	sanitize_payload_json,
)


def test_sanitize_strips_script_and_handlers():
	raw = '<p onclick="alert(1)">ok</p><script>evil()</script><a href="javascript:alert(1)">x</a>'
	out = sanitize_html_fragment(raw)
	assert "<script" not in out.lower()
	assert "onclick" not in out.lower()
	assert "javascript:" not in out.lower()
	assert "ok" in out


def test_sanitize_payload_html_keys():
	payload = {
		"extraTermsHtml": '<img src=x onerror=alert(1)><p>Условия</p>',
		"customer": {"inn": "1"},
	}
	clean = sanitize_payload_json(payload)
	assert clean is not None
	assert "onerror" not in clean["extraTermsHtml"].lower()
	assert "Условия" in clean["extraTermsHtml"]
	assert clean["customer"]["inn"] == "1"


def test_assert_payload_size_raises():
	huge = {"bodyHtml": "x" * 250_000}
	try:
		assert_payload_size(huge)
		assert False, "expected ValueError"
	except ValueError:
		pass
