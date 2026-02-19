from sqlalchemy import create_engine, text
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'finance.db')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def add_columns():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE assets ADD COLUMN contract_size FLOAT DEFAULT 1.0"))
            print("Added contract_size column.")
        except Exception as e:
            print(f"contract_size might already exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE assets ADD COLUMN margin FLOAT DEFAULT 0.0"))
            print("Added margin column.")
        except Exception as e:
            print(f"margin might already exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE assets ADD COLUMN name STRING"))
            print("Added name column.")
        except Exception as e:
            print(f"name might already exist: {e}")

if __name__ == "__main__":
    add_columns()
