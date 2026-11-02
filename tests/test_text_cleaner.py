import pytest
from src.components.text_cleaner import TextNormalizer


@pytest.fixture
def normalizer():
    return TextNormalizer()


def test_urls_and_html_removal(normalizer):
    raw_text = "<p>Pothole on main road http://maps.google.com/xyz123</p>"
    expected = "pothole on main road"
    assert normalizer.normalize(raw_text) == expected


def test_special_characters_and_whitespace(normalizer):
    raw_text = "  Water   supply---interrupted @ ward 4!!  "
    expected = "water supplyinterrupted ward 4"
    assert normalizer.normalize(raw_text) == expected


def test_english_standardization(normalizer):
    raw_text = "STREETLIGHT BROKEN in Sector 9."
    expected = "streetlight broken in sector 9"
    assert normalizer.normalize(raw_text) == expected


def test_devanagari_preservation(normalizer):
    raw_text = "सड़क खराब है!!! कृपया 123 देखें।"
    expected = "सड़क खराब है कृपया 123 देखें"
    assert normalizer.normalize(raw_text) == expected


def test_invalid_inputs(normalizer):
    assert normalizer.normalize("") == ""
    assert normalizer.normalize(None) == ""
    assert normalizer.normalize(123) == ""