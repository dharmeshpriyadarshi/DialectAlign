import os
import sys
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from dataclasses import dataclass

from src.logger import logging
from src.exception import CustomException
from src.components.text_cleaner import TextNormalizer
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    """
    Configuration defining file paths for serialized preprocessing objects.
    """
    preprocessor_obj_file_path: str = os.path.join('artifacts', 'preprocessor.pkl')
    label_encoder_file_path: str = os.path.join('artifacts', 'label_encoder.pkl')

class DataTransformation:
    def __init__(self):
        self.transformation_config = DataTransformationConfig()

    def get_data_transformer_objects(self):
        """
        Constructs and returns the text normalizer and label encoder objects.
        """
        try:
            logging.info("Instantiating TextNormalizer and LabelEncoder.")
            text_normalizer = TextNormalizer()
            label_encoder = LabelEncoder()
            
            return text_normalizer, label_encoder
            
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_path: str, test_path: str):
        """
        Applies the preprocessing pipeline to the train and test datasets.
        (Implementation deferred to Task 2).
        """
        pass