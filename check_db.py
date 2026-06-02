import sqlite3

users = [
    ("Usman", "usman@gmail.com", "123456789"),
    ("Ahmed", "ahmed@gmail.com", "03001234567"),
    ("Sara", "sara@gmail.com", "03005556666")
]

conn = sqlite3.connect("cart.db")

for user in users:
    conn.execute("""
    INSERT INTO users (name, email, phone)
    VALUES (?, ?, ?)
    """, user)

conn.commit()
conn.close()