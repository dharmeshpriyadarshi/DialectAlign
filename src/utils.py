import os
import sys
import pickle
from src.logger import logging
from src.exception import CustomException

def save_object(file_path: str, obj: object) -> None:
    """
    Serializes and saves a Python object to the specified file path.
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
            
        logging.info(f"Object successfully saved at: {file_path}")

    except Exception as e:
        raise CustomException(e, sys)

def load_object(file_path: str) -> object:
    """
    Loads and deserializes a Python object from the specified file path.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
            
        with open(file_path, "rb") as file_obj:
            obj = pickle.load(file_obj)
            
        logging.info(f"Object successfully loaded from: {file_path}")
        return obj

    except Exception as e:
        raise CustomException(e, sys)