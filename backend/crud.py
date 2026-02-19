from sqlalchemy.orm import Session
from . import models, schemas

def get_assets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Asset).offset(skip).limit(limit).all()

def create_asset(db: Session, asset: schemas.AssetCreate):
    db_asset = models.Asset(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def delete_asset(db: Session, asset_id: int):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset:
        db.delete(db_asset)
        db.commit()
        return True
    return False

def update_asset(db: Session, asset_id: int, asset: schemas.AssetCreate):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset:
        for key, value in asset.dict().items():
            setattr(db_asset, key, value)
        db.commit()
        db.refresh(db_asset)
        return db_asset
    return None

def get_net_worth_history(db: Session, skip: int = 0, limit: int = 30):
    return db.query(models.NetWorthHistory).order_by(models.NetWorthHistory.date.desc()).offset(skip).limit(limit).all()

def create_net_worth_history(db: Session, history: schemas.NetWorthHistoryBase):
    db_history = models.NetWorthHistory(**history.dict())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_realized_pnl(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.RealizedProfitLoss).order_by(models.RealizedProfitLoss.date.desc()).offset(skip).limit(limit).all()

def create_realized_pnl(db: Session, pnl: schemas.RealizedPnLCreate):
    db_pnl = models.RealizedProfitLoss(**pnl.dict())
    db.add(db_pnl)
    db.commit()
    db.refresh(db_pnl)
    return db_pnl

from sqlalchemy import func

def get_cumulative_pnl(db: Session):
    # Returns list of (date, daily_pnl, cumulative_pnl)
    # SQLite doesn't support window functions easily in older versions or via simple ORM without subqueries sometimes.
    # But let's try to do it in Python for simplicity if dataset is small, or use window function if supported.
    # Let's fetch all and compute in python for now to be safe and simple.
    results = db.query(models.RealizedProfitLoss).order_by(models.RealizedProfitLoss.date).all()
    
    cumulative_data = []
    running_total = 0.0
    
    # Group by date first
    daily_pnl = {}
    for row in results:
        if row.date not in daily_pnl:
            daily_pnl[row.date] = 0.0
        daily_pnl[row.date] += row.pnl
        
    sorted_dates = sorted(daily_pnl.keys())
    for d in sorted_dates:
        pnl = daily_pnl[d]
        running_total += pnl
        cumulative_data.append({
            "date": d,
            "daily_pnl": pnl,
            "cumulative_pnl": running_total
        })
        
    return cumulative_data

def create_future_transaction(db: Session, transaction: schemas.TransactionCreate):
    # 1. Record the transaction
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    
    # 2. Update or Create Asset
    # Find existing asset with same symbol and contract_month
    existing_asset = db.query(models.Asset).filter(
        models.Asset.symbol == transaction.symbol,
        models.Asset.contract_month == transaction.contract_month,
        models.Asset.type == transaction.asset_type
    ).first()

    if existing_asset:
        # Update existing asset
        # Calculate new weighted average cost
        # Formula: (old_cost * old_qty + new_price * new_qty) / (old_qty + new_qty)
        # Note: For futures, "cost" usually refers to the price at which you opened the position.
        # If we are adding to a position (same direction), we average.
        # If we are closing (opposite direction), we might need different logic, but for now let's assume "Action" handling
        # For simplicity in this step as per requirements: "Update Average Cost... ((1345 * 1) + (1075 * 1)) / 2 = 1210"
        
        total_cost = (existing_asset.cost * existing_asset.quantity) + (transaction.price * transaction.quantity)
        total_qty = existing_asset.quantity + transaction.quantity
        
        if total_qty != 0:
            existing_asset.cost = total_cost / total_qty
        else:
            existing_asset.cost = 0 # Should not happen if we only add, but good for safety
            
        existing_asset.quantity = total_qty
        existing_asset.margin += transaction.assigned_margin # Add margin if assigned
        
        # Update leverage info if needed (though leverage is usually calculated dynamically based on current price)
        # But we store 'leverage' field in Asset, maybe we update it? 
        # The requirement says: "Update Leverage... Numerator: (Price * 100 * 2) / Denominator: (Account Equity)"
        # This seems to be a display-time calculation, but we can update the asset's leverage field if it's intended to be static or a snapshot.
        # However, the user said "System backend should mark this transaction as 'using remaining margin'".
        # For now, let's just update the basic fields.
        
    else:
        # Create new asset
        new_asset = models.Asset(
            type=transaction.asset_type,
            symbol=transaction.symbol,
            quantity=transaction.quantity,
            cost=transaction.price,
            currency="TWD", # Futures usually settled in TWD
            contract_size=transaction.multiplier,
            margin=transaction.assigned_margin,
            contract_month=transaction.contract_month,
            name=f"{transaction.symbol} {transaction.contract_month}"
        )
        db.add(new_asset)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
