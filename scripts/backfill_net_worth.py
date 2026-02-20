import sys
import os
import time
from datetime import datetime, timedelta, date
import pandas as pd
import yfinance as yf
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import SessionLocal
from backend.models import Transaction, NetWorthHistory, Asset
from backend.services import get_usd_to_twd_rate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_historical_prices(symbols, start_date, end_date):
    """
    Fetch historical daily close prices using yfinance.
    Returns a dict mapping symbol to a pd.Series of dates and prices.
    """
    history_map = {}
    
    # We add one day to end_date because yfinance end date is exclusive
    end_date_str = (end_date + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    for symbol_type, symbol in symbols:
        # Construct yfinance symbol
        yf_symbol = symbol
        if symbol_type == "TW_STOCK":
            # Map known TW symbols (very simplified, usually need specific fallback or mapping for Futures)
            if symbol == "QSF":
                yf_symbol = "8299.TW"
            elif symbol == "TX":
                yf_symbol = "2330.TW"
            elif symbol == "MTX":
                yf_symbol = "^TWII"
            elif symbol == "ZEF":
                yf_symbol = "2303.TW"
            else:
                # Try .TW suffix first, assuming .TW works for most standard TW stocks for backfill
                yf_symbol = f"{symbol}.TW"
                
        elif symbol_type == "US_STOCK":
            yf_symbol = symbol
            
        else:
            # Skip Cash or Unknown
            continue
            
        logger.info(f"Downloading history for {yf_symbol}...")
        try:
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(start=start_date_str, end=end_date_str)
            
            if data.empty and symbol_type == "TW_STOCK" and not "TWO" in yf_symbol:
                 # Retry with .TWO for OTC stocks
                 yf_symbol = f"{symbol}.TWO"
                 ticker = yf.Ticker(yf_symbol)
                 data = ticker.history(start=start_date_str, end=end_date_str)
                 
            if not data.empty:
                # Localize timezone to naive date for matching
                data.index = data.index.tz_localize(None).date
                history_map[symbol] = data['Close']
            else:
                logger.warning(f"No data found for {yf_symbol}")
                history_map[symbol] = pd.Series(dtype=float)
        except Exception as e:
            logger.error(f"Error fetching {yf_symbol}: {e}")
            history_map[symbol] = pd.Series(dtype=float)
            
    return history_map

def backfill_net_worth():
    session = SessionLocal()
    try:
        # Get all transactions
        txns = session.query(Transaction).order_by(Transaction.date, Transaction.id).all()
        if not txns:
            logger.info("No transactions found.")
            return

        start_date = txns[0].date
        end_date = datetime.today().date()
        
        logger.info(f"Backfilling from {start_date} to {end_date}")
        
        # Identify all symbols ever traded
        symbols_traded = set((t.asset_type, t.symbol) for t in txns)
        
        # Pre-fetch historical data
        hist_prices = fetch_historical_prices(symbols_traded, start_date, end_date)
        
        # We need a fallback USD/TWD rate. We'll fetch current and use it as a flat rate, 
        # or fetch historical USD/TWD too. For accuracy, fetch historical USD/TWD.
        try:
            usd_hist = yf.Ticker("TWD=X").history(start=start_date.strftime('%Y-%m-%d'), 
                                                  end=(end_date + timedelta(days=1)).strftime('%Y-%m-%d'))
            usd_hist.index = usd_hist.index.tz_localize(None).date
            usd_rates = usd_hist['Close']
        except Exception:
            usd_rates = pd.Series(dtype=float)
        
        current_flat_usd_rate = get_usd_to_twd_rate()

        # Calculate historical net cash flow to determine Initial Cash
        assets_meta = {a.symbol: a for a in session.query(Asset).all()}
        
        total_cash_flow_twd = 0.0
        total_cash_flow_usd = 0.0
        for t in txns:
            flow = t.quantity * t.price
            if t.action in ["BUY", "BUY_OPEN", "BUY_DT"]:
                flow_amount = -flow - t.fee
            else:
                flow_amount = flow - t.fee - t.tax
                
            if t.asset_type in ["TW_STOCK", "TW_FUTURE"]:
                total_cash_flow_twd += flow_amount
            elif t.asset_type == "US_STOCK":
                total_cash_flow_usd += flow_amount

        current_cash_twd = sum(a.quantity for a in assets_meta.values() if a.type == "TWD")
        current_cash_usd = sum(a.quantity for a in assets_meta.values() if a.type == "USD")

        running_twd = current_cash_twd - total_cash_flow_twd
        running_usd = current_cash_usd - total_cash_flow_usd

        # Replay transactions day by day
        # tracking inventory, average cost for realized PnL/equity logic
        
        # state: symbol -> {qty: float, cost: float, type: str, leverage: float, contract_size: float}
        inventory = {}
        
        # Empty old net_worth_history
        session.query(NetWorthHistory).delete()
        
        txn_idx = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Process all transactions for the current date
            while txn_idx < len(txns) and txns[txn_idx].date == current_date:
                t = txns[txn_idx]
                sym = t.symbol
                if sym not in inventory:
                    meta = assets_meta.get(sym)
                    inventory[sym] = {
                        "qty": 0.0, 
                        "cost": 0.0, 
                        "type": t.asset_type,
                        "leverage": meta.leverage if meta and meta.leverage is not None else 1.0,
                        "contract_size": meta.contract_size if meta and meta.contract_size is not None else 1.0,
                        "margin": meta.margin if meta and meta.margin is not None else 0.0
                    }
                    
                inv = inventory[sym]
                action = t.action.upper()
                
                # Update running cash dynamically
                flow = t.quantity * t.price
                if action in ["BUY", "BUY_OPEN", "BUY_DT"]:
                    flow_amount = -flow - t.fee
                else:
                    flow_amount = flow - t.fee - t.tax
                    
                if t.asset_type in ["TW_STOCK", "TW_FUTURE"]:
                    running_twd += flow_amount
                elif t.asset_type == "US_STOCK":
                    running_usd += flow_amount
                
                if action in ["BUY", "BUY_OPEN"]:
                    total_cost = (inv["qty"] * inv["cost"]) + (t.quantity * t.price)
                    inv["qty"] += t.quantity
                    inv["cost"] = total_cost / inv["qty"] if inv["qty"] > 0 else 0.0
                elif action in ["SELL", "SELL_CLOSE"]:
                    inv["qty"] -= t.quantity
                    if inv["qty"] <= 0:
                        inv["qty"] = 0.0
                        inv["cost"] = 0.0
                        
                elif action in ["BUY_DT", "SELL_DT"]:
                    pass
                    
                txn_idx += 1
                
            # Now calculate net worth for current_date
            total_twd = 0.0
            total_usd = 0.0
            details = []
            
            # Get today's USD/TWD rate
            # If weekend/holiday, forward-fill from last available
            # We'll do a simple fallback: find the closest past date
            def get_rate_on_date(rates_series, target_date, default_val):
                # Look backwards up to 30 days to mitigate missing API data
                for i in range(30):
                    d = target_date - timedelta(days=i)
                    if d in rates_series and not pd.isna(rates_series[d]):
                        return rates_series[d]
                return default_val

            usd_rate = get_rate_on_date(usd_rates, current_date, current_flat_usd_rate)
            
            # Calculate total for each asset in inventory
            for sym, inv in inventory.items():
                qty = inv["qty"]
                if qty == 0:
                    continue
                    
                # To calculate real net worth, we need Cash mapping too. 
                # Does the system track TWD/USD manually in transactions? No, usually through separate sync.
                # Since the user said "包含未實現損益，現金未修改則沿用" (use current cash if unchanged).
                # We will fetch current static cash from Assets table
                pass

            # Inject Dynamic Cash tracked via transactions
            details.append({"symbol": "TWD", "type": "TWD", "quantity": running_twd, "value_twd": running_twd})
            total_twd += running_twd

            val_usd_in_twd = running_usd * usd_rate
            details.append({"symbol": "USD", "type": "USD", "quantity": running_usd, "value_twd": val_usd_in_twd})
            total_twd += val_usd_in_twd
            total_usd += running_usd

            # Sum up securities
            for sym, inv in inventory.items():
                qty = inv["qty"]
                if qty <= 0:
                    continue
                    
                a_type = inv["type"]
                price = 0.0
                
                # Get historical price
                if a_type in ["TW_STOCK", "US_STOCK", "TW_FUTURE"]:
                    series = hist_prices.get(sym, pd.Series(dtype=float))
                    price = get_rate_on_date(series, current_date, inv["cost"]) # fallback to cost if no price ever
                
                val_twd = 0.0
                if a_type == "US_STOCK":
                    val_usd = price * qty
                    val_twd = val_usd * usd_rate
                    total_usd += val_usd
                elif a_type == "TW_STOCK":
                    val_twd = price * qty
                elif a_type == "TW_FUTURE":
                    # Equity = Margin + PnL
                    # PnL = (price - cost) * qty * contract_size
                    pnl = (price - inv["cost"]) * qty * inv["contract_size"]
                    val_twd = inv["margin"] + pnl
                    
                total_twd += val_twd
                details.append({
                    "symbol": sym,
                    "type": a_type,
                    "quantity": qty,
                    "cost": inv["cost"],
                    "current_price": price,
                    "value_twd": val_twd
                })
                
            # Save daily record
            record = NetWorthHistory(
                date=current_date,
                total_twd=total_twd,
                total_usd=total_usd,
                details=details
            )
            session.add(record)
            
            current_date += timedelta(days=1)
            
        session.commit()
        logger.info(f"Successfully backfilled net worth up to {end_date}.")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error backfilling: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    backfill_net_worth()
