from typing import List
import pandas as pd
import re
from datetime import datetime
from .base import BaseImporter, TransactionDTO

class UsBrokerStrategy(BaseImporter):
    """
    Concrete Strategy for parsing US Broker CSV files.
    """

    def _read_file(self, file_path: str) -> pd.DataFrame:
        """
        Overrides BaseImporter to read only the transaction details section.
        """
        encodings = ['utf-8', 'big5']
        
        for enc in encodings:
            try:
                # Read line by line to find the transaction headers row
                with open(file_path, 'r', encoding=enc) as f:
                    lines = f.readlines()
                
                start_idx = 0
                for idx, line in enumerate(lines):
                    if '交易日期' in line and '商品代號' in line and '交易種類' in line:
                        start_idx = idx
                        break
                
                # Now use pandas to read from that starting line
                import io
                csv_data = "".join(lines[start_idx:])
                return pd.read_csv(io.StringIO(csv_data))
                
            except UnicodeDecodeError:
                continue
                
        raise ValueError("Could not decode CSV file with supported encodings.")

    def _extract_data(self, df: pd.DataFrame) -> List[dict]:

        """
        Extracts relevant rows and converts to a list of dictionaries.
        """
        records = df.to_dict('records')
        return records

    def _standardize(self, raw_data: List[dict]) -> List[TransactionDTO]:
        """
        Maps raw dictionary data to TransactionDTO.
        """
        transactions = []
        
        # Start matching the required date bounds (2025/11/30 to 2026/02/20)
        start_date = datetime(2025, 11, 30).date()
        end_date = datetime(2026, 2, 20).date()

        for row in raw_data:
            def get_val(key):
                val = row.get(key)
                if isinstance(val, str):
                    return val.strip()
                return val

            # Parse Date
            date_str = get_val('交易日期')
            # If not found or empty, it could be a header row inside the CSV or footer
            if not date_str or not isinstance(date_str, str):
                continue
                
            try:
                txn_date = datetime.strptime(date_str, "%Y/%m/%d").date()
            except (ValueError, TypeError):
                # Try another layout, if it fails then skip
                continue
                
            # Filter date range
            if not (start_date <= txn_date <= end_date):
                continue

            # Parse Action
            raw_action = get_val('交易種類')
            action = "UNKNOWN"
            if raw_action == "買進":
                action = "BUY"
            elif raw_action == "賣出":
                action = "SELL"
            # we will skip "除息" (dividends) or other non-trade actions for now as the schema supports BUY/SELL
            else:
                continue
                
            # Parse Symbol
            symbol = get_val('商品代號')
            if not symbol or symbol == '商品代號':
                continue
            
            # Parse Numeric Fields
            try: 
                quantity = float(str(get_val('股數')).replace(',', ''))
                price = float(str(get_val('價格')).replace(',', ''))
                fee = float(str(get_val('手續費')).replace(',', ''))
                # For US stocks there might be no tax field, or '其他費用' serves as fee/tax
                other_fee = float(str(get_val('其他費用')).replace(',', ''))
                total_fee = fee + other_fee
            except (ValueError, AttributeError, TypeError):
                continue

            dto = TransactionDTO(
                date=txn_date,
                asset_type="US_STOCK", # Marked as US stock
                symbol=symbol,
                action=action,
                price=price,
                quantity=quantity,
                contract_month=None,
                multiplier=1.0, # 1 for US stocks
                fee=total_fee,
                tax=0.0,
                assigned_margin=0.0
            )
            transactions.append(dto)
            
        return transactions
