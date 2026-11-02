import pytest
from src.components.text_cleaner import TextNormalizer, RegionalStandardizer

@pytest.fixture
def normalizer():
    return TextNormalizer()

@pytest.fixture
def standardizer():
    return RegionalStandardizer()

# --- Existing Tests ---
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

# --- New Regional Standardizer Tests ---
def test_civic_noun_standardization(standardizer):
    # Tests mapping of "सरक" -> "सड़क" and "कचरावा" -> "कचरा" while preserving "बा"
    raw_text = "सरक पर कचरावा बा"
    expected = "सड़क पर कचरा बा"
    assert standardizer.standardize_nouns(raw_text) == expected

def test_unmapped_words_preservation(standardizer):
    # Words not in the lexicon map must return entirely unchanged
    raw_text = "ई ठीके बा"
    expected = "ई ठीके बा"
    assert standardizer.standardize_nouns(raw_text) == expected

def test_full_normalization_pipeline(normalizer):
    # End-to-End: HTML strip + Punctuation strip + Lexicon Map + Lowercase
    raw_text = "<p>सरक बहुत खराप बा!!! http://test.com</p>"
    expected = "सड़क बहुत खराब बा"
    assert normalizer.normalize(raw_text) == expected