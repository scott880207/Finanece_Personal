import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as connection:
        # 1. Add column if not exists
        try:
            connection.execute(text("ALTER TABLE assets ADD COLUMN leverage FLOAT DEFAULT 1.0"))
            print("Added 'leverage' column.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")

        # 2. Update specific assets
        # 00685L -> 2.0
        # GGLL -> 2.0
        # Cash (TWD, USD) -> 0.0 (Logic will be handled in service, but let's set DB too for clarity if we want)
        # Actually, let's keep default 1.0 for stocks, but for specific ones set to 2.0.
        # For Cash, strictly speaking leverage is 0? Or 1 (1:1 exposure)?
        # Usually Cash has 0 market exposure. But let's handle Cash logic in code to be safe, 
        # or set it to 0.0 in DB. Let's set to 0.0 for TWD/USD types.
        
        updates = [
            ("UPDATE assets SET leverage = 2.0 WHERE symbol = '00685L'", "00685L"),
            ("UPDATE assets SET leverage = 2.0 WHERE symbol = 'GGLL'", "GGLL"),
            ("UPDATE assets SET leverage = 0.0 WHERE type IN ('TWD', 'USD')", "Cash"),
        ]
        
        for sql, name in updates:
            try:
                result = connection.execute(text(sql))
                print(f"Updated {name}: {result.rowcount} rows affected.")
            except Exception as e:
                print(f"Error updating {name}: {e}")
                
        connection.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
