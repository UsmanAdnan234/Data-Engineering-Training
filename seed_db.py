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

# Users (5 total — tests use user_id 1, 2, 3; user_id 999 must NOT exist)
cur.executemany(
    "INSERT INTO users (name, email, phone) VALUES (%s, %s, %s)",
    [
        ("Asad",     "asad@gmail.com",     "03345678910"),  # user_id 1
        ("Muzammil", "muzammil@gmail.com", "03001234588"),  # user_id 2
        ("Zainab",   "zainab@gmail.com",   "03005556677"),  # user_id 3
        ("Ali",      "ali@gmail.com",      "03112223344"),  # user_id 4
        ("Sara",     "sara@gmail.com",     "03223334455"),  # user_id 5
    ]
)

# Products (5 total)
cur.executemany(
    "INSERT INTO products (name) VALUES (%s)",
    [
        ("T-Shirt",),   # product_id 1
        ("Jeans",),     # product_id 2
        ("Sneakers",),  # product_id 3
        ("Hoodie",),    # product_id 4
        ("Cap",),       # product_id 5
    ]
)

# Variants (product_id, color, size, price, stock)
# CRITICAL stocks required by tests:
#   variant_id 5  → stock=10  (TC-19a adds 7, TC-19b tries +5 → exceeds 10)
#   variant_id 6  → stock=8   (TC-18 tries qty=10 → exceeds 8)
#   variant_id 7  → stock=5   (TC-14 adds exactly 5; TC-41 checks out → stock→0;
#                               TC-42 and TC-50 verify INSUFFICIENT_STOCK)
cur.executemany(
    "INSERT INTO product_variants (product_id, color, size, price, stock) VALUES (%s, %s, %s, %s, %s)",
    [
        (1, "White", "S",      499.99,  50),  # variant_id 1  — used by TC-11,12,TC-48
        (1, "Black", "M",      499.99,  30),  # variant_id 2  — used by SETUP TC-17
        (1, "Red",   "L",      549.99,  20),  # variant_id 3  — used by SETUP TC-35
        (2, "Blue",  "30",    1999.00,  15),  # variant_id 4  — used by TC-13,TC-48
        (2, "Black", "32",    2199.00,  10),  # variant_id 5  — stock=10 (TC-19a/b)
        (3, "White", "42",    3499.00,   8),  # variant_id 6  — stock=8  (TC-18)
        (3, "Black", "43",    3499.00,   5),  # variant_id 7  — stock=5  (TC-14,TC-41,TC-42,TC-50)
        (4, "Gray",  "S",     1499.00,  25),  # variant_id 8
        (4, "Black", "M",     1599.00,  20),  # variant_id 9
        (4, "Navy",  "L",     1599.00,  15),  # variant_id 10
        (5, "Black", "Free",   299.00, 100),  # variant_id 11
        (5, "White", "Free",   299.00,  80),  # variant_id 12
        (5, "Red",   "Free",   349.00,  60),  # variant_id 13
    ]
)

conn.commit()
cur.close()
conn.close()

print("Database seeded successfully.")
print("Users: 5  |  Products: 5  |  Variants: 13  |  Carts: 0  |  Items: 0")
print()
print("Critical variant stocks for tests:")
print("  variant_id 5  stock=10  (TC-19a/b accumulated exceed)")
print("  variant_id 6  stock=8   (TC-18 insufficient stock)")
print("  variant_id 7  stock=5   (TC-14 exact stock; TC-41/42/50 deduction)")
