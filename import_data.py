import sys
import os

# Add backend directory to path to import models
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend import models, database, schemas, crud, services
from sqlalchemy.orm import Session
import yfinance as yf
import pandas as pd

def get_price(symbol):
    try:
        # Try yfinance with .TW
        ticker = yf.Ticker(f"{symbol}.TW")
        data = ticker.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]

        # Try yfinance with .TWO (for TPEX)
        ticker = yf.Ticker(f"{symbol}.TWO")
        data = ticker.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
        
        # Try without suffix
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
            
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
    return None


