"""
Run this before every test session to reset the DB to a clean, known state.
Usage: python seed_db.py
"""
import psycopg2

from app.core.config import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Reset all tables and restart auto-increment sequences
cur.execute("""
    TRUNCATE cart_items, carts, product_variants, products, users
    RESTART IDENTITY CASCADE
""")

# Users
cur.executemany(
    "INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)",
    [
        ("Asad",     "asad@gmail.com",     "03345678910"),
        ("Muzammil", "muzammil@gmail.com", "03001234588"),
        ("Zainab",   "zainab@gmail.com",   "03005556677"),
    ]
)

# Products
cur.executemany(
    "INSERT INTO products (name) VALUES (%s)",
    [("T-Shirt",), ("Jeans",), ("Sneakers",)]
)

# Variants (product_id, color, size, price, stock)
cur.executemany(
    "INSERT INTO product_variants (product_id, color, size, price, stock) VALUES (%s, %s, %s, %s, %s)",
    [
        (1, "White", "S",  499.99, 50),
        (1, "Black", "M",  499.99, 30),
        (1, "Red",   "L",  549.99, 20),
        (2, "Blue",  "30", 1999.00, 15),
        (2, "Black", "32", 2199.00, 10),
        (3, "White", "42", 3499.00, 8),
        (3, "Black", "43", 3499.00, 5),
    ]
)

conn.commit()
cur.close()
conn.close()

print("Database seeded successfully.")
print("Users: 3  |  Products: 3  |  Variants: 7  |  Carts: 0  |  Items: 0")
