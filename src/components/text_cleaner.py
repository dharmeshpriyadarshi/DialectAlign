import re
import sys
from src.logger import logging
from src.exception import CustomException

class RegionalStandardizer:
    """
    Handles deterministic spelling standardization for Bhojpuri/Maithili 
    civic vocabulary. Normalizes nouns to reduce OOV rates while 
    preserving dialectical verbs and syntax.
    """
    def __init__(self):
        # High-frequency civic noun normalizations
        self.civic_lexicon_map = {
            "सरक": "सड़क",
            "सडक": "सड़क",
            "खराप": "खराब",
            "पनिया": "पानी",
            "जलकल": "पानी",
            "बिजुलिया": "बिजली",
            "कचरावा": "कचरा",
            "कचड़ा": "कचरा",
            "नालिया": "नाला",
            "नल्ली": "नाला"
        }

    def standardize_nouns(self, text: str) -> str:
        try:
            words = text.split()
            standardized_words = [self.civic_lexicon_map.get(word, word) for word in words]
            return " ".join(standardized_words)
        except Exception as e:
            raise CustomException(e, sys)


class TextNormalizer:
    """
    Handles deterministic noise removal and string standardization for cross-lingual corpora.
    Preserves Devanagari Unicode blocks for Indic languages.
    """
    def __init__(self):
        self.standardizer = RegionalStandardizer()

    @staticmethod
    def remove_urls_and_tags(text: str) -> str:
        try:
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            text = re.sub(r'<.*?>', '', text)
            return text
        except Exception as e:
            raise CustomException(e, sys)

    @staticmethod
    def remove_noise_preserve_indic(text: str) -> str:
        try:
            # Preserve alphanumeric, whitespaces, and Devanagari block (\u0900-\u097F)
            text = re.sub(r'[^\w\s\u0900-\u097F]', '', text)
            # Remove Devanagari specific punctuation (Danda and Double Danda)
            text = re.sub(r'[\u0964\u0965]', '', text)
            # Normalize multi-spaces into single spaces
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            raise CustomException(e, sys)

    def normalize(self, text: str) -> str:
        """
        Executes the full text normalization pipeline including regional standardization.
        """
        try:
            if not isinstance(text, str):
                return ""
            
            text = self.remove_urls_and_tags(text)
            text = self.remove_noise_preserve_indic(text)
            text = self.standardizer.standardize_nouns(text)
            
            return text.lower()
            
        except Exception as e:
            raise CustomException(e, sys)