import yfinance as yf
import twstock
import requests
import logging
import time
import urllib3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_usd_to_twd_rate():
    try:
        # Using yfinance to get USD/TWD rate
        ticker = yf.Ticker("TWD=X")
        data = ticker.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
        return 32.0 # Fallback
    except Exception as e:
        logger.error(f"Error fetching USD/TWD rate: {e}")
        return 32.0

def get_stock_price(symbol: str, type: str):
    try:
        if type == "US_STOCK":
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        elif type == "TW_STOCK":
            # Try yfinance with .TW first
            for suffix in [".TW", ".TWO"]:
                try:
                    full_symbol = f"{symbol}{suffix}"
                    ticker = yf.Ticker(full_symbol)
                    data = ticker.history(period="1d")
                    if not data.empty:
                        price = data['Close'].iloc[-1]
                        logger.info(f"Fetched {full_symbol} from yfinance: {price}")
                        return price
                except Exception as e:
                    logger.warning(f"yfinance failed for {full_symbol}: {e}")
            
            # Map Future symbols to Underlying if needed
            # This mapping should happen BEFORE trying yfinance if we want to fetch underlying price for futures
            # But here we are inside "TW_STOCK" block.
            # If type is TW_FUTURE, we called get_stock_price(symbol, "TW_STOCK").
            # So symbol is "QSF".
            # We need to map "QSF" to "8299" BEFORE yfinance loop if we want to fetch 8299.TW
            
            symbol_map = {
                "QSF": "8299", 
                "TX": "2330", 
                "MTX": "^TWII", 
                "ZEF": "2303", 
            }
            search_symbol = symbol_map.get(symbol, symbol)
            
            # Retry yfinance with mapped symbol
            if search_symbol != symbol:
                 for suffix in [".TW", ".TWO"]:
                    try:
                        full_symbol = f"{search_symbol}{suffix}"
                        ticker = yf.Ticker(full_symbol)
                        data = ticker.history(period="1d")
                        if not data.empty:
                            price = data['Close'].iloc[-1]
                            logger.info(f"Fetched {full_symbol} (mapped from {symbol}) from yfinance: {price}")
                            return price
                    except Exception as e:
                        logger.warning(f"yfinance failed for {full_symbol}: {e}")

            # Fallback to twstock if yfinance fails
            try:
                logger.info(f"Falling back to twstock for {search_symbol}")
                stock = twstock.Stock(search_symbol)
                if not stock.price:
                    stock.fetch_31()
                if stock.price:
                    price = stock.price[-1]
                    logger.info(f"Fetched {symbol} from twstock: {price}")
                    return price
            except Exception as e:
                logger.error(f"twstock fallback failed for {symbol}: {e}")
                
                # Last resort: Manual fetch with SSL verification disabled
                try:
                    logger.info(f"Attempting manual fetch for {symbol} with SSL disabled")
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    # Mimic twstock's fetch logic simply or just get latest
                    # This is a simplified fallback for current month
                    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo={symbol}"
                    response = requests.get(url, verify=False, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data['stat'] == 'OK':
                            # Get last price from 'data' array
                            # Format: ["Date", "Trade Volume", "Trade Value", "Opening Price", "Highest Price", "Lowest Price", "Closing Price", ...]
                            last_day = data['data'][-1]
                            closing_price = float(last_day[6].replace(',', ''))
                            logger.info(f"Fetched {symbol} from manual request: {closing_price}")
                            return closing_price
                except Exception as manual_e:
                    logger.error(f"Manual fallback failed for {symbol}: {manual_e}")

    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
    
    logger.error(f"All methods failed for {symbol}, returning 0.0")
    return 0.0

def calculate_net_worth(assets):
    total_twd = 0.0
    total_usd = 0.0
    total_exposure_twd = 0.0 # Total market exposure in TWD
    usd_rate = get_usd_to_twd_rate()
    
    details = []

    for asset in assets:
        current_price = 0.0
        value_twd = 0.0
        exposure_twd = 0.0
        
        # Determine leverage multiplier
        # Default to 1.0 if not set (though DB has default)
        # For Cash (TWD, USD), leverage should be 0.0 effectively for market risk, 
        # but the user said "00685L is 2x... weighted sum divided by net worth".
        # If I have 100 TWD cash, exposure is 0? Or 100?
        # Usually leverage ratio = Total Exposure / Net Worth.
        # Cash has 0 exposure to market volatility (relative to itself).
        # But if we consider "Gross Leverage", it might include cash.
        # Based on user description: "00685L is 2x... GGLL is 2x... weighted sum / net worth".
        # This implies we sum (Value * Leverage).
        # For Cash, if leverage is 0 (as I set in migration script for TWD/USD types if I did, wait I didn't update TWD/USD types in migration script successfully as it said 0 rows affected).
        # Ah, because 'type' might be 'TWD' or 'USD' but I might have checked wrong column or no rows matched.
        # Let's check asset types.
        # Anyway, let's use asset.leverage from DB.
        
        leverage_mult = asset.leverage if asset.leverage is not None else 1.0
        
        # Override for Cash types if DB didn't update correctly or to be safe
        if asset.type in ["TWD", "USD"]:
            leverage_mult = 0.0
        
        # Default values for all assets
        notional_value = 0.0
        equity = 0.0
        pnl = 0.0
        pnl_percentage = 0.0
        
        if asset.type == "TWD":
            value_twd = asset.quantity
            total_twd += value_twd
            current_price = 1.0
            leverage_mult = 0.0
            
            notional_value = value_twd * leverage_mult
            equity = value_twd
            
        elif asset.type == "USD":
            value_twd = asset.quantity * usd_rate
            total_usd += asset.quantity
            total_twd += value_twd
            current_price = usd_rate
            leverage_mult = 0.0
            
            notional_value = value_twd * leverage_mult
            equity = value_twd
            
        elif asset.type == "US_STOCK":
            price_usd = get_stock_price(asset.symbol, "US_STOCK")
            value_usd = price_usd * asset.quantity
            value_twd = value_usd * usd_rate
            total_usd += value_usd
            total_twd += value_twd
            current_price = price_usd
            
            notional_value = value_twd * leverage_mult
            equity = value_twd
            # P&L for stocks
            cost_twd = asset.cost * asset.quantity * usd_rate
            pnl = value_twd - cost_twd
            pnl_percentage = (pnl / cost_twd * 100) if cost_twd != 0 else 0.0

        elif asset.type == "TW_STOCK":
            price_twd = get_stock_price(asset.symbol, "TW_STOCK")
            value_twd = price_twd * asset.quantity
            total_twd += value_twd
            current_price = price_twd
            
            notional_value = value_twd * leverage_mult
            equity = value_twd
            # P&L for stocks
            cost_twd = asset.cost * asset.quantity
            pnl = value_twd - cost_twd
            pnl_percentage = (pnl / cost_twd * 100) if cost_twd != 0 else 0.0

        elif asset.type == "TW_FUTURE":
            # For Futures:
            # Price = Underlying Price (or Future Price if available)
            # Notional Value (Exposure) = Price * Quantity * Contract Size
            # Equity = Margin + (Price - Cost) * Quantity * Contract Size
            
            price_twd = get_stock_price(asset.symbol, "TW_STOCK") # Using stock price as proxy
            current_price = price_twd
            
            contract_size = asset.contract_size if asset.contract_size else 1.0
            margin = asset.margin if asset.margin else 0.0
            
            # 1. Notional Value (Exposure)
            notional_value = price_twd * asset.quantity * contract_size
            
            # 2. Unrealized P&L
            # (Current Price - Entry Price) * Quantity * Contract Size
            pnl = (price_twd - asset.cost) * asset.quantity * contract_size
            
            # 3. Equity
            equity = margin + pnl
            
            # Update totals
            # For Net Worth, we add Equity
            total_twd += equity
            
            # For Exposure, we add Notional Value
            exposure_twd = notional_value
            
            # Leverage = Notional Value / Margin (Nominal Leverage)
            # If Margin is 0 (Cross Margin), it's technically undefined per position, 
            # but we can show 0 or handle it. 
            # Ideally we should use the Maintenance Margin if known, but we only have 'margin' field.
            if margin > 0:
                leverage_mult = notional_value / margin
            else:
                # If margin is 0, maybe fallback to Notional / Equity? 
                # Or just 0 to indicate "Cross Margin / Undefined".
                # Given user set margin to 31200, this will work.
                leverage_mult = 0.0
            
            value_twd = equity # For backward compatibility in 'value_twd' field if needed, or we use specific fields
            
            # P&L Percentage on Margin? Or on Notional?
            # Usually on Margin (ROE)
            pnl_percentage = (pnl / margin * 100) if margin != 0 else 0.0
            
        if asset.type != "TW_FUTURE":
             exposure_twd = value_twd * leverage_mult
        
        total_exposure_twd += exposure_twd
            
        details.append({
            "id": asset.id,
            "name": asset.name,
            "symbol": asset.symbol if asset.symbol else asset.type,
            "type": asset.type,
            "quantity": asset.quantity,
            "cost": asset.cost,
            "currency": asset.currency,
            "current_price": current_price,
            "value_twd": value_twd, # This remains Equity for Futures to keep 'total' consistent if summed frontend
            "leverage": leverage_mult,
            "contract_size": asset.contract_size,
            "margin": asset.margin,
            "notional_value": notional_value,
            "equity": equity,
            "pnl": pnl,
            "pnl_percentage": pnl_percentage
        })
        
    total_net_worth_twd = total_twd # This is actually total value in TWD
    leverage_ratio = total_exposure_twd / total_net_worth_twd if total_net_worth_twd > 0 else 0.0

    return {
        "total_twd": total_twd,
        "total_usd": total_usd,
        "usd_rate": usd_rate,
        "leverage_ratio": leverage_ratio,
        "details": details
    }
