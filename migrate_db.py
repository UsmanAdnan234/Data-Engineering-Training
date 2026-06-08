import sqlite3

from app.core.config import DB_NAME

conn = sqlite3.connect(DB_NAME)
try:
    conn.execute(
        "ALTER TABLE carts ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'"
    )
    conn.commit()
    print("Migration complete: status column added to carts table")
except Exception as e:
    print(f"Migration skipped: {e}")
finally:
    conn.close()
