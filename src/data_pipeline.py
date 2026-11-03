import os
import sys
import pandas as pd

from src.logger import logging
from src.exception import CustomException
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.utils import load_object

def run_pipeline():
    try:
        logging.info("--- Starting Data Pipeline Execution ---")
        
        # Validation Setup: Generate synthetic data if real data is absent
        dummy_data_path = os.path.join("data", "raw", "dummy_civic_data.csv")
        os.makedirs(os.path.dirname(dummy_data_path), exist_ok=True)
        
        if not os.path.exists(dummy_data_path):
            logging.info("Generating synthetic dataset for pipeline validation.")
            df = pd.DataFrame({
                "text": [
                    "Pothole on main street", "Water supply interrupted", 
                    "Garbage uncollected", "Streetlight broken", 
                    "Road caved in", "Power outage", "Pipeline burst"
                ],
                "label": [
                    "infrastructure", "utility", 
                    "sanitation", "infrastructure", 
                    "infrastructure", "utility", "utility"
                ]
            })
            df.to_csv(dummy_data_path, index=False)

        # Stage 1: Data Ingestion
        logging.info("--- Stage 1: Data Ingestion ---")
        ingestion = DataIngestion()
        train_path, test_path = ingestion.initiate_data_ingestion(source_data_path=dummy_data_path)
        
        logging.info(f"Ingestion complete. Train path: {train_path} | Test path: {test_path}")

        # Stage 2: Data Transformation
        logging.info("--- Stage 2: Data Transformation ---")
        transformation = DataTransformation()
        train_df, test_df, preprocessor_path, encoder_path = transformation.initiate_data_transformation(
            train_path=train_path, 
            test_path=test_path
        )
        
        logging.info(f"Transformation complete. Train shape: {train_df.shape} | Test shape: {test_df.shape}")

        # Stage 3: Artifact Deserialization Verification
        logging.info("--- Stage 3: Artifact Deserialization Verification ---")
        loaded_preprocessor = load_object(file_path=preprocessor_path)
        loaded_encoder = load_object(file_path=encoder_path)

        logging.info(f"Preprocessor loaded successfully. Type: {type(loaded_preprocessor)}")
        logging.info(f"LabelEncoder loaded successfully. Classes mapped: {loaded_encoder.classes_}")

        logging.info("--- Pipeline Execution Successful ---")

    except Exception as e:
        logging.error("Pipeline execution failed.")
        raise CustomException(e, sys)

if __name__ == "__main__":
    run_pipeline()