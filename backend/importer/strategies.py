from typing import List, Any
import pandas as pd
import re
from datetime import datetime
from .base import BaseImporter, TransactionDTO

class TwBrokerStrategy(BaseImporter):
    """
    Concrete Strategy for parsing Taiwan Broker CSV files.
    """

    def _extract_data(self, df: pd.DataFrame) -> List[dict]:
        """
        Extracts relevant rows and converts to a list of dictionaries.
        """
        # Based on the user prompt, columns might contain tabs like '\t類別'
        # The base class _clean_headers should have removed the tabs from the keys.
        # However, data fields might also contain tabs or whitespace.
        
        # We process the DataFrame row by row
        records = df.to_dict('records')
        return records

    def _standardize(self, raw_data: List[dict]) -> List[TransactionDTO]:
        """
        Maps raw dictionary data to TransactionDTO.
        """
        transactions = []
        
        for row in raw_data:
            # Helper to safely get value and strip
            def get_val(key):
                val = row.get(key)
                if isinstance(val, str):
                    return val.strip()
                return val

            # Parse Date
            date_str = get_val('成交日期')
            try:
                txn_date = datetime.strptime(date_str, "%Y/%m/%d").date()
            except (ValueError, TypeError):
                # Skip invalid dates or headers repeated in body
                continue

            # Parse Action
            raw_action = get_val('類別')
            action = "UNKNOWN"
            if raw_action == "現股買進":
                action = "BUY"
            elif raw_action == "現股賣出":
                action = "SELL"
            elif raw_action == "融券買進": # Short cover
                action = "BUY_CLOSE"
            elif raw_action == "融券賣出": # Short sell
                action = "SELL_OPEN"
                
            # Parse Symbol
            raw_symbol = get_val('股票名稱')
            # Ensure safe string conversion
            if raw_symbol is None:
                continue
            
            # Handle potential numeric values or numpy types
            raw_symbol_str = str(raw_symbol).strip()

            # Extract content inside parentheses or match alphanumeric code
            # e.g., "元大美債20正2(00680L)" -> "00680L"
            symbol_match = re.search(r'\((.*?)\)', raw_symbol_str)
            if symbol_match:
                symbol = symbol_match.group(1)
            else:
                symbol = raw_symbol_str
            
            # Parse Numeric Fields
            try: 
                quantity = float(str(get_val('股數')).replace(',', ''))
                price = float(str(get_val('成交價')).replace(',', ''))
                fee = float(str(get_val('手續費')).replace(',', ''))
                tax = float(str(get_val('交易稅')).replace(',', ''))
            except (ValueError, AttributeError):
                continue # Skip rows with non-numeric data

            dto = TransactionDTO(
                date=txn_date,
                asset_type="Stock", # Hardcoded as per requirements
                symbol=symbol,
                action=action,
                price=price,
                quantity=quantity,
                contract_month=None,
                multiplier=1.0,
                fee=fee,
                tax=tax,
                assigned_margin=0.0
            )
            transactions.append(dto)
            
        return transactions
