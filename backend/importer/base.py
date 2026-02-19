from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Any
import pandas as pd
from datetime import date

@dataclass
class TransactionDTO:
    date: date
    asset_type: str
    symbol: str
    action: str
    price: float
    quantity: float
    contract_month: Optional[str] = None
    multiplier: float = 1.0
    fee: float = 0.0
    tax: float = 0.0
    assigned_margin: float = 0.0

class BaseImporter(ABC):
    """
    Abstract Base Class for Broker Importers using Template Method Pattern.
    """

    def parse(self, file_path: str) -> List[TransactionDTO]:
        """
        Template method defining the algorithm structure.
        """
        df = self._read_file(file_path)
        df = self._clean_headers(df)
        raw_data = self._extract_data(df)
        transactions = self._standardize(raw_data)
        return transactions

    def _read_file(self, file_path: str) -> pd.DataFrame:
        """
        Reads CSV or Excel file. Default implementation for CSV.
        """
        # Attempt to read with different encodings if standard utf-8 fails
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding='big5') # Common for TW brokers

    def _clean_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Removes whitespace/tabs from column names.
        """
        df.columns = df.columns.str.strip().str.replace('\t', '')
        return df

    @abstractmethod
    def _extract_data(self, df: pd.DataFrame) -> List[Any]:
        """
        Extract raw data from DataFrame. To be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _standardize(self, raw_data: List[Any]) -> List[TransactionDTO]:
        """
        Convert raw data to TransactionDTO list. To be implemented by subclasses.
        """
        pass
