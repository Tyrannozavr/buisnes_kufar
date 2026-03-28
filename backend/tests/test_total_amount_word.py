"""Тесты прописи суммы сделки (рубли / копейки)."""
import pytest

from app.api.purchases.utils.total_amount_word import format_total_amount_word


def test_format_total_amount_word_zero():
	s = format_total_amount_word(0.0)
	assert "рубл" in s.lower()
	assert "копе" in s.lower()


def test_format_total_amount_word_known_sum():
	s = format_total_amount_word(1123.75)
	assert "тысяч" in s.lower()
	assert "рубл" in s.lower()
	assert "копе" in s.lower()
	assert "семьдесят пять" in s or "75" in s  # num2words пишет копейки словами


def test_format_total_amount_word_rounding():
	s = format_total_amount_word(10.996)
	assert "одиннадцать" in s.lower() or "11" in s


def test_format_total_amount_word_none_and_invalid():
	assert format_total_amount_word(None) == ""
	assert format_total_amount_word(float("nan")) == ""


def test_format_total_amount_word_negative_clamped():
	s = format_total_amount_word(-100.0)
	s0 = format_total_amount_word(0.0)
	assert s == s0
