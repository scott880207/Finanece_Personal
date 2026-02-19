from sqlalchemy import Column, Integer, String, Float, Date, JSON
from .database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)  # TWD, USD, TW_STOCK, US_STOCK
    symbol = Column(String, index=True, nullable=True)
    quantity = Column(Float)
    cost = Column(Float) # Average cost per unit
    currency = Column(String, default="TWD") # Currency of the asset value
    leverage = Column(Float, default=1.0) # Leverage multiplier (e.g., 2.0 for 2x ETF)
    contract_size = Column(Float, default=1.0)
    margin = Column(Float, default=0.0)
    name = Column(String, nullable=True)
    contract_month = Column(String, nullable=True) # YYYYMM for Futures

class NetWorthHistory(Base):
    __tablename__ = "net_worth_history"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, unique=True)
    total_twd = Column(Float)
    total_usd = Column(Float)
    details = Column(JSON) # Snapshot of asset values

class RealizedProfitLoss(Base):
    __tablename__ = "realized_pnl"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    symbol = Column(String, index=True)
    quantity = Column(Float)
    pnl = Column(Float)
    notes = Column(String, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    asset_type = Column(String)
    symbol = Column(String, index=True)
    action = Column(String) # BUY_OPEN, SELL_OPEN, SELL_CLOSE, BUY_CLOSE
    price = Column(Float)
    quantity = Column(Float)
    contract_month = Column(String, nullable=True)
    multiplier = Column(Float, default=1.0)
    fee = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    assigned_margin = Column(Float, default=0.0)

