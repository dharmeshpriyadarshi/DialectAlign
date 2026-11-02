import re
import sys
from src.logger import logging
from src.exception import CustomException


class TextNormalizer:
    """
    Handles deterministic noise removal and string standardization
    for cross-lingual corpora.
    Preserves Devanagari Unicode blocks for Indic languages.
    """

    def __init__(self):
        pass

    @staticmethod
    def remove_urls_and_tags(text: str) -> str:
        try:
            # Strip web artifacts
            text = re.sub(
                r'http\S+|www\S+|https\S+',
                '',
                text,
                flags=re.MULTILINE
            )
            text = re.sub(r'<.*?>', '', text)
            return text
        except Exception as e:
            raise CustomException(e, sys)

    @staticmethod
    def remove_noise_preserve_indic(text: str) -> str:
        try:
            # Preserve alphanumeric, whitespaces, and Devanagari block
            text = re.sub(r'[^\w\s\u0900-\u097F]', '', text)

            # Normalize multi-spaces into single spaces
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            raise CustomException(e, sys)

    def normalize(self, text: str) -> str:
        """
        Executes the full text normalization pipeline.
        """
        try:
            if not isinstance(text, str):
                return ""

            text = self.remove_urls_and_tags(text)
            text = self.remove_noise_preserve_indic(text)

            return text.lower()

        except Exception as e:
            raise CustomException(e, sys)