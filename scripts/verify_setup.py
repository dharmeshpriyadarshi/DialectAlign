import os
import sys
from src.logger import logging
from src.exception import CustomException
from src.utils import save_object

def verify_infrastructure():
    try:
        logging.info("Starting infrastructure verification protocol.")
        
        # Test 1: Object Serialization
        dummy_data = {"status": "infrastructure_verified", "version": 1.0}
        dummy_path = os.path.join("artifacts", "dummy.pkl")
        save_object(file_path=dummy_path, obj=dummy_data)
        logging.info("Serialization test passed.")

        # Test 2: Custom Exception Trigger
        logging.info("Initiating deliberate exception for traceback verification.")
        trigger_error = 1 / 0  # Deliberate ZeroDivisionError

    except Exception as e:
        custom_error = CustomException(e, sys)
        logging.error(custom_error)
        print(f"\n[Verification Complete] Intercepted Error:\n{custom_error}\n")
        print("Check the logs/ directory to ensure this traceback was securely recorded.")

if __name__ == "__main__":
    verify_infrastructure()