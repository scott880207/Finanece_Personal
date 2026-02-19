from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the parent directory to sys.path to allow importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Asset
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'finance.db')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_assets():
    db = SessionLocal()
    assets = db.query(Asset).all()
    print(f"Total assets found: {len(assets)}")
    for asset in assets:
        print(f"ID: {asset.id}, Type: {asset.type}, Symbol: {asset.symbol}, Quantity: {asset.quantity}, Cost: {asset.cost}, Currency: {asset.currency}")
    db.close()

if __name__ == "__main__":
    check_assets()
