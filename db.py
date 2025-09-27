import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False, future=True)

def run_query(query, params=None, fetch=False):
    """Run a raw SQL query.
    - query: SQL string (use :param for placeholders)
    - params: dict of parameters
    - fetch: True to return results
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        if fetch:
            return result.fetchall()
        conn.commit()