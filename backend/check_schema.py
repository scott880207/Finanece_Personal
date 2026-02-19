from sqlalchemy import create_engine, inspect
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'finance.db')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('assets')]

if 'leverage' in columns:
    print("Column 'leverage' exists.")
else:
    print("Column 'leverage' does NOT exist.")
