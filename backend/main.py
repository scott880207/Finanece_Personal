from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud, services, database
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/assets/", response_model=schemas.Asset)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(database.get_db)):
    return crud.create_asset(db=db, asset=asset)

@app.get("/assets/", response_model=List[schemas.Asset])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    assets = crud.get_assets(db, skip=skip, limit=limit)
    return assets

@app.delete("/assets/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_asset(db, asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"status": "success"}

@app.put("/assets/{asset_id}", response_model=schemas.Asset)
def update_asset(asset_id: int, asset: schemas.AssetCreate, db: Session = Depends(database.get_db)):
    updated_asset = crud.update_asset(db, asset_id, asset)
    if not updated_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return updated_asset

@app.get("/net-worth/current")
def get_current_net_worth(db: Session = Depends(database.get_db)):
    assets = crud.get_assets(db)
    return services.calculate_net_worth(assets)

@app.get("/net-worth/history", response_model=List[schemas.NetWorthHistory])
def read_net_worth_history(skip: int = 0, limit: int = 1000, db: Session = Depends(database.get_db)):
    return crud.get_net_worth_history(db, skip=skip, limit=limit)

@app.get("/pnl/history", response_model=List[schemas.RealizedPnL])
def read_pnl_history(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_realized_pnl(db, skip=skip, limit=limit)

@app.post("/pnl/", response_model=schemas.RealizedPnL)
def create_pnl(pnl: schemas.RealizedPnLCreate, db: Session = Depends(database.get_db)):
    return crud.create_realized_pnl(db, pnl)

@app.get("/pnl/cumulative")
def read_cumulative_pnl(db: Session = Depends(database.get_db)):
    return crud.get_cumulative_pnl(db)

@app.post("/transactions/future", response_model=schemas.Transaction)
def create_future_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(database.get_db)):
    return crud.create_future_transaction(db, transaction)


from fastapi import UploadFile, File, Form
import shutil
import os
from .importer import TwBrokerStrategy, TransactionProcessor
from .importer.us_strategies import UsBrokerStrategy
from .services import update_assets_from_history

@app.post("/upload/history")
async def upload_history(
    file: UploadFile = File(...),
    strategy: str = Form(...),
    db: Session = Depends(database.get_db)
):
    # 1. Save file temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Select Strategy
        # Supports "cathay" (TW) and "us_broker" (US)
        if strategy.lower() == "cathay":
            importer = TwBrokerStrategy()
        elif strategy.lower() == "us_broker":
            importer = UsBrokerStrategy()
        else:
            # Default to TW if unknown, but better to support both forms
            importer = TwBrokerStrategy()
            
        # 3. Parse and Process
        transactions = importer.parse(file_path)
        processor = TransactionProcessor()
        count = processor.process_transactions(transactions, db)
        
        # 4. Update Assets
        update_assets_from_history(db)
        
        return {"status": "success", "imported_count": count, "message": "Import successful and assets updated."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

def record_net_worth_job():
    db = database.SessionLocal()
    try:
        assets = crud.get_assets(db)
        data = services.calculate_net_worth(assets)
        
        history_entry = schemas.NetWorthHistoryBase(
            date=datetime.now().date(),
            total_twd=data["total_twd"],
            total_usd=data["total_usd"],
            details=data["details"]
        )
        # Check if entry for today exists to avoid duplicates or error
        # For simplicity, we might just try to create and catch error, or check first.
        # crud.create_net_worth_history handles creation.
        # Ideally check if exists.
        existing = db.query(models.NetWorthHistory).filter(models.NetWorthHistory.date == datetime.now().date()).first()
        if not existing:
            crud.create_net_worth_history(db, history_entry)
        else:
            # Update existing
            existing.total_twd = data["total_twd"]
            existing.total_usd = data["total_usd"]
            existing.details = data["details"]
            db.commit()
            
    except Exception as e:
        print(f"Error in scheduled job: {e}")
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    scheduler = BackgroundScheduler()
    # Run every day at 13:30 (after TW market close) or 16:00 (after US market close... wait US close is 4am TW time next day)
    # Let's set it to run at 14:00 TW time for now.
    scheduler.add_job(record_net_worth_job, 'cron', hour=14, minute=0)
    scheduler.start()

