import sys
import os
import logging
from backend.importer.strategies import TwBrokerStrategy
from backend.importer.processor import TransactionProcessor
from unittest.mock import MagicMock

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verification.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def verify_import(file_path):
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return

    logging.info(f"Starting import verification for: {file_path}")

    # 1. Parse
    try:
        strategy = TwBrokerStrategy()
        transactions = strategy.parse(file_path)
        logging.info(f"Successfully parsed {len(transactions)} transactions.")
        
        if transactions:
            logging.info("Sample parsed transaction:")
            logging.info(transactions[0])
    except Exception as e:
        logging.error(f"Parsing failed: {e}")
        return

    # 2. Process (Mock DB)
    try:
        processor = TransactionProcessor()
        mock_session = MagicMock()
        # Mock duplicate check to always return False (simulate fresh insert)
        mock_session.query.return_value.scalar.return_value = False
        
        count = processor.process_transactions(transactions, mock_session)
        logging.info(f"Processor would insert {count} transactions.")
        
        # Verify calls
        logging.info(f"DB Add called {mock_session.add.call_count} times.")
        logging.info(f"DB Commit called {mock_session.commit.call_count} times.")
        
    except Exception as e:
        logging.error(f"Processing failed: {e}")

if __name__ == "__main__":
    file_path = r"d:\Finanece_Personal\csv_for_import\20250101_20250218_record.csv"
    verify_import(file_path)
