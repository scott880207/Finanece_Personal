import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.importer.us_strategies import UsBrokerStrategy
from backend.importer.processor import TransactionProcessor
from backend.database import SessionLocal
from backend.models import Transaction, RealizedProfitLoss

def run_import():
    # 1. Parse
    strategy = UsBrokerStrategy()
    file_path = "d:/Finanece_Personal/csv_for_import/US_20251130_20260220.csv"
    transactions = strategy.parse(file_path)
    print(f"Parsed {len(transactions)} transactions.")

    session = SessionLocal()
    try:
        # First, insert the transactions
        processor = TransactionProcessor()
        inserted = processor.process_transactions(transactions, session)
        print(f"Inserted {inserted} new transactions into the database.")
        
        # Next, compute Realized PnL using FIFO for each symbol processed
        symbols_processed = set(t.symbol for t in transactions if t.action in ('SELL', 'SELL_CLOSE'))
        
        for symbol in symbols_processed:
            # Get all buys and sells for this symbol, ordered by date and id
            txns = session.query(Transaction).filter(
                Transaction.symbol == symbol,
                Transaction.asset_type == 'US_STOCK'
            ).order_by(Transaction.date, Transaction.id).all()
            
            # Simple FIFO queue for buys: [{"qty": float, "price": float}]
            buy_queue = []
            
            # Keep track of which sell transactions have already been realized to avoid duplication
            # This requires checking the realized_pnl table, but to keep it correct, we can calculate
            # from scratch and overwrite, or just map what sells we already processed.
            # Easiest way: drop all realized_pnl for this symbol and re-insert them all based on full history.
            session.query(RealizedProfitLoss).filter(RealizedProfitLoss.symbol == symbol).delete()
            
            for t in txns:
                if t.action in ('BUY', 'BUY_OPEN'):
                    buy_queue.append({"qty": t.quantity, "price": t.price})
                elif t.action in ('SELL', 'SELL_CLOSE'):
                    sell_qty = t.quantity
                    sell_price = t.price
                    realized_pnl = 0.0
                    
                    while sell_qty > 0:
                        if not buy_queue:
                            # We sold more than we bought in DB!
                            # Assume cost basis = 0 for the remainder
                            realized_pnl += (sell_price - 0) * sell_qty
                            sell_qty = 0
                            break
                        
                        buy_lot = buy_queue[0]
                        buy_price = buy_lot["price"]
                        
                        if buy_lot["qty"] <= sell_qty:
                            # Consume the whole lot
                            qty_to_match = buy_lot["qty"]
                            realized_pnl += (sell_price - buy_price) * qty_to_match
                            sell_qty -= qty_to_match
                            buy_queue.pop(0)
                        else:
                            # Partially consume the lot
                            qty_to_match = sell_qty
                            realized_pnl += (sell_price - buy_price) * qty_to_match
                            buy_lot["qty"] -= qty_to_match
                            sell_qty = 0
                            
                    # Subtract trailing fee if we want exact net PnL, assuming fee is per transaction.
                    # PnL = realized_pnl - commission
                    net_pnl = realized_pnl - t.fee
                    
                    # Insert into RealizedProfitLoss
                    rpl = RealizedProfitLoss(
                        date=t.date,
                        symbol=t.symbol,
                        quantity=t.quantity,
                        pnl=net_pnl,
                        notes="US Stock FIFO PnL (including fees)"
                    )
                    session.add(rpl)

        from backend.services import update_assets_from_history
        update_assets_from_history(session)
        session.commit()
        print("Realized PnL calculated and Assets updated successfully.")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_import()
