from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import date

class AssetBase(BaseModel):
    type: str
    symbol: Optional[str] = None
    quantity: float
    cost: float
    currency: str = "TWD"
    leverage: Optional[float] = 1.0
    contract_size: Optional[float] = 1.0
    margin: Optional[float] = 0.0
    name: Optional[str] = None
    contract_month: Optional[str] = None

    @field_validator('symbol', 'name', mode='before')
    @classmethod
    def cast_to_string(cls, v):
        if v is not None:
            return str(v)
        return v

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int

    class Config:
        from_attributes = True

class NetWorthHistoryBase(BaseModel):
    date: date
    total_twd: float
    total_usd: float
    details: List[Dict[str, Any]]

class NetWorthHistory(NetWorthHistoryBase):
    id: int

    class Config:
        from_attributes = True

class RealizedPnLBase(BaseModel):
    date: date
    symbol: str
    quantity: float
    pnl: float
    notes: Optional[str] = None

class RealizedPnLCreate(RealizedPnLBase):
    pass

class RealizedPnL(RealizedPnLBase):
    id: int

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    date: date
    asset_type: str
    symbol: str
    action: str
    price: float
    quantity: float
    contract_month: Optional[str] = None
    multiplier: Optional[float] = 1.0
    fee: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    assigned_margin: Optional[float] = 0.0

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int

    class Config:
        from_attributes = True

