import os
from dataclasses import dataclass

@dataclass
class DataIngestionConfig:
    """
    Configuration class defining the file paths for data ingestion outputs.
    """
    train_data_path: str = os.path.join('artifacts', 'train.csv')
    test_data_path: str = os.path.join('artifacts', 'test.csv')
    raw_data_path: str = os.path.join('artifacts', 'data.csv')