import sqlite3

conn = sqlite3.connect("cart.db")

with open("app/database/schema.sql") as f:
    conn.executescript(f.read())

conn.commit()
conn.close()

print("Database created successfully")