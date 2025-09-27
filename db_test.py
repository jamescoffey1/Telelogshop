import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Test query
with engine.connect() as conn:
    result = conn.execute(text("SELECT NOW();"))
    print("✅ Connected! Time on DB server:", result.fetchone())