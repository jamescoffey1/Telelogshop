from db import run_query

# Ensure table exists
run_query("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    balance NUMERIC DEFAULT 0
)
""")

# Insert a test user
run_query(
    "INSERT INTO users (username, balance) VALUES (:username, :balance) ON CONFLICT (username) DO NOTHING",
    {"username": "James", "balance": 100}
)

# Read back users
rows = run_query("SELECT * FROM users", fetch=True)
print("Users in DB:", rows)