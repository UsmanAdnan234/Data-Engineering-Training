import sqlite3
from app.core.config import DB_NAME

conn = sqlite3.connect(DB_NAME)

with open("app/database/schema.sql") as f:
    conn.executescript(f.read())

conn.commit()
conn.close()

print("Database created successfully")