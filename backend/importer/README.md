# Backend Importer Module

This module handles the import of transaction data from brokerage CSV files into the database.

## Structure

- `base.py`: Contains the `BaseImporter` abstract base class and `TransactionDTO`.
- `strategies.py`: Contains concrete implementation of import strategies (e.g., `TwBrokerStrategy`).
- `processor.py`: Contains `TransactionProcessor` for database operations and idempotency checks.

## How to Extend

To add support for a new broker (e.g., US Broker like Firstrade) or new asset types (e.g., Futures), follow these steps:

### 1. Create a New Strategy Class

In `backend/importer/strategies.py` (or a new file), create a class that inherits from `BaseImporter`.

```python
from .base import BaseImporter, TransactionDTO
import pandas as pd
from datetime import datetime

class FirstradeStrategy(BaseImporter):
    def _extract_data(self, df: pd.DataFrame) -> List[dict]:
        # Implement extraction logic specific to Firstrade CSV format
        return df.to_dict('records')

    def _standardize(self, raw_data: List[dict]) -> List[TransactionDTO]:
        transactions = []
        for row in raw_data:
            # Map fields
            # ...
            dto = TransactionDTO(
                date=...,
                asset_type="Stock", # or "US_Stock"
                symbol=...,
                action=..., # Map "Buy" -> "BUY", "Sell" -> "SELL"
                price=...,
                quantity=...,
                fee=...,
                # ...
            )
            transactions.append(dto)
        return transactions
```

### 2. Handle Asset Types

For Futures, ensure you populate `asset_type="Future"` and parsing `contract_month` (e.g., "202506") and `multiplier` (e.g., 200 for TX) correctly in the `TransactionDTO`.

### 3. Register the Strategy

You can then use the new strategy in your application logic:

```python
importer = FirstradeStrategy()
transactions = importer.parse("path/to/firstrade.csv")
processor.process_transactions(transactions, db_session)
```
