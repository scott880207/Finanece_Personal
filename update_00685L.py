import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.database import SessionLocal
from backend.models import Transaction, RealizedProfitLoss, Asset
from backend.importer.strategies import TwBrokerStrategy
from backend.importer.processor import TransactionProcessor

def update_00685L():
    session = SessionLocal()
    try:
        # 1. Clear out corrupted data for 00685L from DB (both US_STOCK false entries and TW_STOCK)
        session.query(Transaction).filter(Transaction.symbol.contains('00685L')).delete()
        session.query(RealizedProfitLoss).filter(RealizedProfitLoss.symbol.contains('00685L')).delete()
        session.query(Asset).filter(Asset.symbol.contains('00685L')).delete()
        session.commit()
        
        # 2. Parse the CSV files
        strategy = TwBrokerStrategy()
        
        # Parse 2025 CSV
        file2 = "d:/Finanece_Personal/csv_for_import/20250219_20260219_record.csv"
        txns2 = strategy.parse(file2)
        
        # Combine and filter ONLY 00685L
        all_txns = [t for t in txns2 if '00685L' in str(t.symbol)]
        
        # 3. Sort by date
        all_txns.sort(key=lambda x: x.date)
        
        # 4. Save to transactions queue
        for dto in all_txns:
            txn = Transaction(
                date=dto.date,
                asset_type="TW_STOCK",
                symbol='00685L',
                action=dto.action,
                price=dto.price,
                quantity=dto.quantity,
                fee=dto.fee,
                tax=dto.tax,
                assigned_margin=0.0
            )
            session.add(txn)
            
        # 5. FIFO PnL simulation (ignore DAY TRADES)
        inventory = 0.0
        total_cost_remaining = 0.0
        buy_queue = []
        
        for t in all_txns:
            if '_DT' in t.action:
                continue
            
            if t.action == 'BUY':
                unit_fee = t.fee / t.quantity if t.quantity > 0 else 0
                buy_queue.append({'qty': t.quantity, 'price': t.price, 'unit_fee': unit_fee})
                inventory += t.quantity
                
            elif t.action == 'SELL':
                sell_qty = t.quantity
                sell_price = t.price
                inventory -= sell_qty
                
                realized_pnl = 0.0
                matched_buy_fees = 0.0
                
                while sell_qty > 0 and buy_queue:
                    buy_lot = buy_queue[0]
                    if buy_lot['qty'] <= sell_qty:
                        qty_to_match = buy_lot['qty']
                        realized_pnl += (sell_price - buy_lot['price']) * qty_to_match
                        matched_buy_fees += qty_to_match * buy_lot['unit_fee']
                        sell_qty -= qty_to_match
                        buy_queue.pop(0)
                    else:
                        qty_to_match = sell_qty
                        realized_pnl += (sell_price - buy_lot['price']) * qty_to_match
                        matched_buy_fees += qty_to_match * buy_lot['unit_fee']
                        buy_lot['qty'] -= qty_to_match
                        sell_qty = 0
                
                net_pnl = realized_pnl - t.fee - t.tax - matched_buy_fees
                
                # Insert DB
                rpl = RealizedProfitLoss(
                    date=t.date,
                    symbol='00685L',
                    quantity=t.quantity,
                    pnl=net_pnl,
                    notes=f"FIFO Gross:{realized_pnl:.0f} matched_buy_fees:{matched_buy_fees:.0f}"
                )
                session.add(rpl)
        
        # 6. Calculate Average Cost for the remaining inventory to store in Assets
        # Remainder in buy_queue:
        if inventory > 0:
            remaining_cost = sum(lot['qty'] * lot['price'] + (lot['qty'] * lot['unit_fee']) for lot in buy_queue)
            avg_cost = remaining_cost / inventory
            
            asset = Asset(
                type="TW_STOCK",
                symbol="00685L",
                quantity=inventory,
                cost=avg_cost,
                currency="TWD",
                name="群益臺灣加權正2"
            )
            session.add(asset)
            
        session.commit()
        print(f"Successfully updated 00685L. Inventory: {inventory}")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_00685L()
