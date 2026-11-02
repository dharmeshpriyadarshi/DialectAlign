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
        """
        try:
            logging.info(f"Loading training data from {train_path}")
            logging.info(f"Loading testing data from {test_path}")
            
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Retrieving preprocessing objects.")
            text_normalizer, label_encoder = self.get_data_transformer_objects()

            logging.info("Applying TextNormalizer to train and test text columns.")
            train_df['text'] = train_df['text'].apply(text_normalizer.normalize)
            test_df['text'] = test_df['text'].apply(text_normalizer.normalize)

            logging.info("Fitting LabelEncoder on training labels and transforming.")
            train_df['label'] = label_encoder.fit_transform(train_df['label'])
            
            logging.info("Transforming testing labels (Strictly NO fitting).")
            test_df['label'] = label_encoder.transform(test_df['label'])

            logging.info("Data transformation applied successfully.")

            return (
                train_df,
                test_df,
                text_normalizer,
                label_encoder
            )

        except Exception as e:
            raise CustomException(e, sys)