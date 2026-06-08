"""
Run once to create all tables in PostgreSQL.
Usage: python init_db.py
After this, use Alembic for any schema changes: alembic upgrade head
"""
import psycopg2

from app.core.config import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)

with open("app/database/schema.sql") as f:
    conn.cursor().execute(f.read())

conn.commit()
conn.close()

print("Tables created successfully.")
